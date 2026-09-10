from typing import Optional
from fastapi import APIRouter, Depends, Response, HTTPException, status
from app.handlers.auth import (
    registration,
    login,
    update,
    remove,
    update_profile_image,
)
from app.models.auth import get_user_by_id, update_username
from app.utils.jwt import (
    get_current_user_id,
    get_user_id_for_refresh,
    create_access_token,
)
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    
class UserValidate(BaseModel):
    email: str
    password: str
    
class UserUpdate(BaseModel):
    name: str
    email: str
    password: str


class UsernameUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None


class UserImageUpdate(BaseModel):
    image_url: str

    

@router.post("/registration")
def usersRegister(data: UserCreate):
    return registration(data.name, data.email, data.password)


@router.post("/login")
def usersLogin(data: UserValidate, response: Response):
    result = login(data.email, data.password)
    if "token" not in result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("message", "Invalid email or password"),
        )
    response.set_cookie(
        key="access_token",
        value=result["token"],
        httponly=True,
        samesite="lax",
        secure=False,  # change to True in production (HTTPS)
        max_age=60 * 60 * 24,
        path="/",
    )
    return {
        "message": "Logged in successfully",
        "access_token": result["token"],
        "token": result["token"],
        "token_type": "bearer",
    }


@router.post("/refresh-token")
@router.post("/refresh")
async def refresh_token_route(
    response: Response,
    user_id: str = Depends(get_user_id_for_refresh),
):
    new_token = create_access_token(user_id)
    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
        path="/",
    )
    return {
        "message": "Token refreshed successfully",
        "access_token": new_token,
        "token": new_token,
        "token_type": "bearer",
    }


@router.get("/getuser")
@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if not user or "error" in user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/update-username")
@router.patch("/update-username")
async def update_username_route(
    data: UsernameUpdate,
    user_id: str = Depends(get_current_user_id),
):
    new_name = (data.name or data.username or "").strip()
    if not new_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty",
        )
    result = update_username(user_id, new_name)
    if not result or "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update username in database",
        )
    return {
        "message": "Username updated successfully",
        "name": new_name,
        "username": new_name,
    }


@router.put("/update-profile-image")
@router.patch("/update-profile-image")
async def update_profile_image_route(
    data: UserImageUpdate,
    user_id: str = Depends(get_current_user_id),
):
    clean_url = (data.image_url or "").strip()
    if not clean_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image_url cannot be empty",
        )
    result = update_profile_image(user_id, clean_url)
    if not result or "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile image in database",
        )
    return {
        "message": "Profile image updated successfully",
        "image_url": clean_url,
    }



@router.put("/updateData/{user_id}")
def usersUpdate(user_id: str, data: UserUpdate):
    return update(user_id, data.name, data.email, data.password)

@router.delete("/removeuser/{user_id}")
def usersDelete(user_id: str):
    return remove(user_id)


