from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from api.auth.hash_password import HashPassword
from api.auth.jwt_handler import verify_access_token
from api.database.connection import users_collection
from api.model.user import Users

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
hash_password=HashPassword()
async def authenticate(token:str=Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    decoded_token=verify_access_token(token)
    user = await get_user(str(decoded_token["sub"]))
    if not user:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return user

async def get_user(username:str)->object:
    return await users_collection.find_one({"username":username})


async def authenticate_user(username: str, password: str) -> object:
    """authenticate user with username and password"""
    user: object =await  get_user(username)
    if not user:
        return None
    if not hash_password.verify_password(password, user.get("password")):
        return None
    return user