from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routes.auth import router as auth_router
from app.routes.photoupload import router as photopostrouter
from app.routes.posts import router as posts_router
from app.routes.noteupload import router as note_router
from app.routes.linkupload import router as link_router
from app.routes.folder import router as folder_router
from app.database.db import check_db_connection
from app.utils.ip_ban import get_client_ip, ip_ban_manager
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.middleware("http")
async def ip_ban_middleware(request: Request, call_next):
    # Exclude CORS preflight requests from ban checks
    if request.method == "OPTIONS":
        return await call_next(request)

    ip = get_client_ip(request)

    # 1. Reject if IP is currently banned
    is_banned, remaining, reason = ip_ban_manager.is_banned(ip)
    if is_banned:
        return JSONResponse(
            status_code=403,
            content={
                "error": "ip_banned",
                "detail": f"Access Denied: Your IP ({ip}) is banned for {remaining} more seconds ({reason}).",
                "remaining_seconds": remaining,
            },
            headers={"Retry-After": str(remaining)},
        )

    # 2. Check if this request triggers an automated velocity flood ban (e.g. > 25 reqs in 10s)
    if request.url.path != "/":
        was_banned, reason = ip_ban_manager.record_request(ip)
        if was_banned:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "ip_banned",
                    "detail": f"Access Denied: Your IP ({ip}) has been banned for {ip_ban_manager.ban_duration_seconds} seconds ({reason}).",
                    "remaining_seconds": ip_ban_manager.ban_duration_seconds,
                },
                headers={"Retry-After": str(ip_ban_manager.ban_duration_seconds)},
            )

    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    check_db_connection()


app.include_router(auth_router)
app.include_router(photopostrouter)
app.include_router(posts_router)
app.include_router(note_router)
app.include_router(link_router)
app.include_router(folder_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://buckethead-seven.vercel.app",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3200",
        "http://localhost:3200",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "API is running server is healthy 🚀"}


@app.get("/api/ip-ban/status")
def get_ip_ban_status():
    return {
        "banned_ips": ip_ban_manager.get_all_banned_ips(),
        "config": {
            "window_seconds": ip_ban_manager.window_seconds,
            "max_requests_in_window": ip_ban_manager.max_requests_in_window,
            "ban_duration_seconds": ip_ban_manager.ban_duration_seconds,
            "max_violations": ip_ban_manager.max_violations,
        },
    }


@app.post("/api/ip-ban/reset")
def reset_ip_bans():
    ip_ban_manager.reset_all()
    return {"message": "All IP bans and request counters have been reset successfully"}


@app.post("/api/ip-ban/unban/{ip}")
def unban_specific_ip(ip: str):
    removed = ip_ban_manager.unban_ip(ip)
    return {
        "ip": ip,
        "unbanned": removed,
        "message": f"IP {ip} unbanned" if removed else f"IP {ip} was not banned",
    }

