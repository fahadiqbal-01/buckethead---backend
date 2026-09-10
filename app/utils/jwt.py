import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status

load_dotenv()

jwt_secrets = os.getenv("JWT_SECRET", "dev-secret-key")
jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")


def create_access_token(user_id: str) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=jwt_expire_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, jwt_secrets, algorithm=jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, jwt_secrets, algorithms=[jwt_algorithm])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_id_from_token(token: str | None) -> str | None:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    return payload.get("sub")


def get_current_user_id(request: Request) -> str:
    """
    Extracts and verifies user ID from JWT token via cookies or Authorization header.
    Strictly validates signature and expiration for protected routes.
    """
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: No access token found in cookie or header",
        )

    try:
        payload = jwt.decode(token, jwt_secrets, algorithms=[jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: User ID missing",
            )
        return str(user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_user_id_for_refresh(request: Request) -> str:
    """
    Extracts user ID from JWT for refresh.
    Verifies cryptographic signature while allowing expired tokens (grace period)
    so the client can obtain a new access token without re-login.
    """
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: No access token found in cookie or header",
        )

    try:
        payload = jwt.decode(
            token,
            jwt_secrets,
            algorithms=[jwt_algorithm],
            options={"verify_exp": False},
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: User ID missing",
            )
        return str(user_id)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token signature",
        )
