from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.handlers.folder import (
    handle_create_space,
    handle_get_user_spaces,
    handle_add_item_to_space,
    handle_remove_item_from_space,
    handle_delete_space,
)
from app.utils.jwt import get_current_user_id
from app.utils.limiter import (
    create_limiter,
    read_limiter,
    modify_limiter,
    delete_limiter,
)

router = APIRouter()


class CreateSpaceRequest(BaseModel):
    folder_name: str = Field(..., min_length=1, max_length=15)
    folder_color: str = Field(..., min_length=1, max_length=7)


class SpaceItemRequest(BaseModel):
    folder_name: str
    post_id: str


@router.post("/createspace", status_code=status.HTTP_201_CREATED, dependencies=[Depends(create_limiter)])
async def create_space_route(
    data: CreateSpaceRequest,
    user_id: str = Depends(get_current_user_id),
):
    result = handle_create_space(
        user_id=user_id,
        folder_name=data.folder_name,
        folder_color=data.folder_color,
    )

    if isinstance(result, dict) and "error" in result:
        if result.get("error") == "space_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.get("details", "Space already exists"),
            )
        detail_msg = result.get("details", result.get("error", "Database error occurred"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create space: {detail_msg}",
        )

    return result


@router.get("/getspaces", dependencies=[Depends(read_limiter)])
async def get_spaces_route(
    user_id: str = Depends(get_current_user_id),
):
    result = handle_get_user_spaces(user_id=user_id)

    if isinstance(result, dict) and "error" in result:
        detail_msg = result.get("details", result.get("error", "Database error occurred"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch spaces: {detail_msg}",
        )

    return result


@router.post("/addtospace", dependencies=[Depends(modify_limiter)])
async def add_item_to_space_route(
    data: SpaceItemRequest,
    user_id: str = Depends(get_current_user_id),
):
    result = handle_add_item_to_space(
        user_id=user_id,
        folder_name=data.folder_name,
        post_id=data.post_id,
    )

    if isinstance(result, dict):
        if result.get("error") == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("details", "Space not found"),
            )
        if "error" in result:
            detail_msg = result.get("details", result.get("error", "Database error occurred"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add item to space: {detail_msg}",
            )

    return result


@router.post("/removefromspace", dependencies=[Depends(modify_limiter)])
async def remove_item_from_space_route(
    data: SpaceItemRequest,
    user_id: str = Depends(get_current_user_id),
):
    result = handle_remove_item_from_space(
        user_id=user_id,
        folder_name=data.folder_name,
        post_id=data.post_id,
    )

    if isinstance(result, dict):
        if result.get("error") == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("details", "Space not found"),
            )
        if "error" in result:
            detail_msg = result.get("details", result.get("error", "Database error occurred"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove item from space: {detail_msg}",
            )

    return result


@router.delete("/deletespace/{folder_name}", dependencies=[Depends(delete_limiter)])
async def delete_space_route(
    folder_name: str,
    user_id: str = Depends(get_current_user_id),
):
    result = handle_delete_space(user_id=user_id, folder_name=folder_name)

    if isinstance(result, dict):
        if result.get("error") == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("details", "Space not found"),
            )
        if "error" in result:
            detail_msg = result.get("details", result.get("error", "Database error occurred"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete space: {detail_msg}",
            )

    return result
