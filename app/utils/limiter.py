import time
from typing import Callable, List, Union
from fastapi import Request, HTTPException, status
from starlette.responses import Response
from starlette.websockets import WebSocket
from pyrate_limiter import (
    BucketFactory,
    AbstractBucket,
    InMemoryBucket,
    RateItem,
    Limiter,
    Rate,
    Duration,
)
from app.utils.jwt import decode_access_token


async def smart_identifier(request: Union[Request, WebSocket]) -> str:
    """
    Identifies the requester for rate-limiting.
    - Uses authenticated user ID if logged in (from cookies or Bearer token).
    - Falls back to the client's real IP address (supporting X-Forwarded-For headers from reverse proxies).
    """
    path = request.scope.get("path", "")
    method = request.scope.get("method", "")

    # 1. Check for authenticated user token
    token = None
    if hasattr(request, "cookies"):
        token = request.cookies.get("access_token")

    if not token and hasattr(request, "headers"):
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

    if token:
        try:
            payload = decode_access_token(token)
            if payload and payload.get("sub"):
                return f"user:{payload.get('sub')}:{method}:{path}"
        except Exception:
            pass

    # 2. Fall back to client IP for unauthenticated routes
    forwarded = request.headers.get("x-forwarded-for") if hasattr(request, "headers") else None
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    elif hasattr(request, "client") and request.client:
        ip = request.client.host
    else:
        ip = "127.0.0.1"

    return f"ip:{ip}:{method}:{path}"


async def rate_limit_callback(_request: Request, _response: Response = None):
    """
    Custom 429 response when rate limit is exceeded.
    Returns HTTP 429 Too Many Requests with Retry-After header.
    Note: _request and _response are required by the FastAPI limiter callback signature.
    """
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests. Please slow down and try again shortly.",
        headers={"Retry-After": "5"},
    )


class MultiBucketFactory(BucketFactory):
    """
    Dynamically routes rate-limiting buckets per user/IP.
    Each unique requester receives its own rate bucket that leaks automatically.
    """

    def __init__(self, rates: Union[Rate, List[Rate]]):
        self.rates = [rates] if isinstance(rates, Rate) else rates
        self.buckets: dict[str, AbstractBucket] = {}

    def wrap_item(self, name: str, weight: int = 1):
        return RateItem(name, int(time.time() * 1000), weight=weight)

    def get(self, item: RateItem) -> AbstractBucket:
        if item.name not in self.buckets:
            bucket = self.create(InMemoryBucket, self.rates)
            self.buckets[item.name] = bucket
        return self.buckets[item.name]


class RateLimiter:
    """
    FastAPI dependency rate limiter powered by pyrate-limiter.
    Compatible with all FastAPI router architectures (including included routers).
    """

    def __init__(
        self,
        limiter: Limiter,
        identifier: Callable = smart_identifier,
        callback: Callable = rate_limit_callback,
        blocking: bool = False,
    ):
        self.limiter = limiter
        self.identifier = identifier
        self.callback = callback
        self.blocking = blocking

    async def __call__(self, request: Request, response: Response = None):
        key = await self.identifier(request)
        success = await self.limiter.try_acquire_async(key, blocking=self.blocking)
        if not success:
            return await self.callback(request, response)


def make_limiter(rate: Union[Rate, List[Rate]]) -> RateLimiter:
    """Factory helper to instantiate a per-requester RateLimiter dependency."""
    factory = MultiBucketFactory(rate)
    return RateLimiter(
        limiter=Limiter(factory),
        identifier=smart_identifier,
        callback=rate_limit_callback,
    )


# --- Professional Rate Limiter Profiles ---

# 1. Auth Limiter: 10 requests per minute (protects against brute force & credential stuffing)
auth_limiter = make_limiter(Rate(10, Duration.MINUTE))

# 2. Creation Limiter: 15 creates per 30 seconds (protects Cloudinary uploads & DB insertion)
create_limiter = make_limiter(Rate(15, Duration.SECOND * 30))

# 3. Modification Limiter: 25 updates per 10 seconds (color updates, space item toggles, profile changes)
modify_limiter = make_limiter(Rate(25, Duration.SECOND * 10))

# 4. Deletion Limiter: 15 deletes per 10 seconds (prevents rapid item/space deletion spam)
delete_limiter = make_limiter(Rate(15, Duration.SECOND * 10))

# 5. Read Limiter: 120 reads per minute (generous allowance for dashboard sync/polling)
read_limiter = make_limiter(Rate(120, Duration.MINUTE))

