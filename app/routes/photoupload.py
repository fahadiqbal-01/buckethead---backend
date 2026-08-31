from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from app.handlers.photoupload import photo_upload
from app.utils.jwt import get_user_id_from_token

router = APIRouter()


class UploadPhotoRequest(BaseModel):
    photo_url: str
    name: str
    note: str = ""


@router.post("/photoupload", status_code=status.HTTP_201_CREATED)
async def upload_photo_route(request: Request, data: UploadPhotoRequest):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: No access token or authorization header provided",
            )
        token = auth_header.split(" ", 1)[1]

    user_id = get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    result = photo_upload(
        user_id=user_id,
        photo_url=data.photo_url,
        name=data.name,
        note=data.note,
    )

    if isinstance(result, dict) and "error" in result:
        detail_msg = result.get("details", result.get("error", "Database error occurred"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save photo: {detail_msg}",
        )

    return result

