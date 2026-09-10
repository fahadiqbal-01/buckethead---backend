from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.handlers.noteupload import note_upload, fetch_user_notes, change_note_color
from app.utils.jwt import get_current_user_id
from app.utils.limiter import create_limiter, read_limiter, modify_limiter

router = APIRouter()


class UploadNoteRequest(BaseModel):
    color: str = "yellow"
    node_title: str
    note_text: str = ""


class UpdateNoteColorRequest(BaseModel):
    color: str


@router.post("/noteupload", status_code=status.HTTP_201_CREATED, dependencies=[Depends(create_limiter)])
async def upload_note_route(
    data: UploadNoteRequest,
    user_id: str = Depends(get_current_user_id),
):
    result = note_upload(
        user_id=user_id,
        color=data.color,
        node_title=data.node_title,
        note_text=data.note_text,
    )

    if isinstance(result, dict) and "error" in result:
        detail_msg = result.get("details", result.get("error", "Database error occurred"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save note: {detail_msg}",
        )

    return result


@router.get("/getnoteuploads", dependencies=[Depends(read_limiter)])
async def get_notes_route(
    user_id: str = Depends(get_current_user_id),
):
    result = fetch_user_notes(user_id)

    if isinstance(result, dict) and "error" in result:
        detail_msg = result.get("details", result.get("error", "Database error occurred"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notes: {detail_msg}",
        )

    return result


@router.patch("/updatenotecolor/{note_id}", dependencies=[Depends(modify_limiter)])
async def update_note_color_route(
    note_id: str,
    data: UpdateNoteColorRequest,
    user_id: str = Depends(get_current_user_id),
):
    result = change_note_color(user_id=user_id, note_id=note_id, color=data.color)

    if isinstance(result, dict):
        if result.get("error") == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("details", "Note not found"),
            )
        if "error" in result:
            detail_msg = result.get("details", result.get("error", "Database error occurred"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update note color: {detail_msg}",
            )

    return result
