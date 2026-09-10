from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.photoupload import router as photopostrouter
from app.routes.posts import router as posts_router
from app.routes.noteupload import router as note_router
from app.routes.linkupload import router as link_router
from app.routes.folder import router as folder_router
from app.database.db import check_db_connection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    check_db_connection()


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(photopostrouter)
app.include_router(posts_router)
app.include_router(note_router)
app.include_router(link_router)
app.include_router(folder_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://buckethead-eta.vercel.app",
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
    return {"message": "API is running 🚀"}