from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.handlers.linkupload import link_upload, fetch_user_links
from app.utils.jwt import get_current_user_id
from app.utils.limiter import create_limiter, read_limiter

router = APIRouter()


class UploadLinkRequest(BaseModel):
    link_name: str
    link_url: str
    image_url: Optional[str] = ""
    link_desc: Optional[str] = ""


@router.post("/linkupload", status_code=status.HTTP_201_CREATED, dependencies=[Depends(create_limiter)])
async def upload_link_route(
    data: UploadLinkRequest,
    user_id: str = Depends(get_current_user_id),
):
    result = link_upload(
        user_id=user_id,
        image_url=data.image_url or "",
        link_name=data.link_name,
        link_url=data.link_url,
        link_desc=data.link_desc or "",
    )

    if isinstance(result, dict) and "error" in result:
        detail_msg = result.get("details", result.get("error", "Database error occurred"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save link: {detail_msg}",
        )

    return result


@router.get("/getlinkuploads", dependencies=[Depends(read_limiter)])
async def get_links_route(
    user_id: str = Depends(get_current_user_id),
):
    result = fetch_user_links(user_id)

    if isinstance(result, dict) and "error" in result:
        detail_msg = result.get("details", result.get("error", "Database error occurred"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch links: {detail_msg}",
        )

    return result
