from fastapi import APIRouter, Depends, HTTPException, status
from app.handlers.posts import fetch_all_user_posts, remove_user_post
from app.utils.jwt import get_current_user_id
from app.utils.limiter import read_limiter, delete_limiter

router = APIRouter()


@router.get("/getallposts", dependencies=[Depends(read_limiter)])
async def get_all_posts_route(
    user_id: str = Depends(get_current_user_id),
):
    result = fetch_all_user_posts(user_id)

    if isinstance(result, dict) and "error" in result:
        detail_msg = result.get("details", result.get("error", "Database error occurred"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch posts: {detail_msg}",
        )

    return result


@router.delete("/deletepost/{post_type}/{post_id}", dependencies=[Depends(delete_limiter)])
async def delete_post_route(
    post_type: str,
    post_id: str,
    user_id: str = Depends(get_current_user_id),
):
    result = remove_user_post(user_id=user_id, post_type=post_type, post_id=post_id)

    if isinstance(result, dict):
        if result.get("error") == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or you are not authorized to delete it",
            )
        if "error" in result:
            detail_msg = result.get("details", result.get("error", "Database error occurred"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete post: {detail_msg}",
            )

    return result
