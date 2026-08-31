import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

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


def get_user_id_from_token(token: str) -> str | None:
    payload = decode_access_token(token)
    if not payload:
        return None
    return payload.get("sub")