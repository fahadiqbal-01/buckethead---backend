from fastapi import APIRouter, Response, HTTPException, status
from app.handlers.auth import registration
from app.handlers.auth import login
from app.handlers.auth import update
from app.handlers.auth import remove
from pydantic import BaseModel

router=APIRouter()

class UserCreate(BaseModel):
    name:str
    email:str
    password:str
    
class UserValidate(BaseModel):
    email:str
    password:str
    
class UserUpdate(BaseModel):
    name:str
    email:str
    password:str
    

@router.post("/registration")

def usersRegister(data:UserCreate):
    return registration(data.name,data.email,data.password)


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


@router.put("/updateData/{user_id}")

def usersUpdate(user_id:str, data:UserUpdate):
    return update(user_id, data.name, data.email, data.password)

@router.delete("/removeuser/{user_id}")
def usersDelete(user_id:str):
    return remove(user_id)

