from app.models import auth as user_reg
from app.models import auth as user_validate
from app.models import auth as user_update
from app.models import auth as user_remove
from app.utils.bcrypt import hash_password
from app.utils import jwt as jwt_auth


def registration(name,email,password):
    hashed_Pass = hash_password(password)
    return user_reg.create_user(name,email,hashed_Pass)

def login(email, password_hash):
    users = user_validate.validate_user(email, password_hash)
    if "id" in users:
        token = jwt_auth.create_access_token(users["id"])
        return{
            "token": token,
            "token_type":"bearer"
        }
    else:
        return {"message":"Invalid email or password"}
        
def update(user_id,name,email,password_hash):
    users = user_update.update_user(user_id,name,email,password_hash)
    if "id" in users:
        return {"id":str(users["id"])}
    else:
        return {"message":"not updating"}
    
def remove(user_id):
    users = user_remove.remove_user(user_id)
    if "id" in users:
        return {"message":"user deleted"}
    else:
        return {"err":"user id incorretc"}


def get_profile(user_id: str):
    return user_reg.get_user_by_id(user_id)


def update_profile_image(user_id: str, image_url: str):
    return user_reg.update_user_image(user_id, image_url)


def update_profile_name(user_id: str, name: str):
    return user_reg.update_username(user_id, name)
