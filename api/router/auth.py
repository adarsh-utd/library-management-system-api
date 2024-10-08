from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import JSONResponse

from api.auth.authenticate import authenticate_user, authenticate
from api.auth.hash_password import HashPassword
from api.auth.jwt_handler import create_access_token
from api.database.connection import  users_collection
from api.model.user import Users, LoginResponseModel, AddUserModel, UserType

auth_router = APIRouter(
    tags=['Authentication'],
    responses={404: {
        "description": "Not found"
    }},
)
hash_password=HashPassword()

@auth_router.post("/login")
async def login( form_data: OAuth2PasswordRequestForm = Depends())-> JSONResponse:
    """
Authenticate a user using  username and password.
If credentials is valid a json response is returned that contain JWT token
    :param form_data: The form data that contains user's credentials (username & password)
    :return JSONResponse: A JSON response that contains status code 200 and content which contains user_id,
    username, user_type and access_token if credentials is valid.
    :raise HTTPException: If login attempts fails with invalid credentials or other errors HTTPException is raised.
    This includes status code and message.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user={"sub": user.get("username")})
    response_model = LoginResponseModel(
        id=str(user.get("_id")),
        username=user.get("username"),
        user_type=user.get("user_type"),
        access_token=access_token
    )
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=jsonable_encoder(response_model))



@auth_router.post("/signup")
async def signup(user:AddUserModel=Body(...))-> JSONResponse:
    """
    Register a new user
    The endpoint allow to  create a new account. If registration is successfully an JSONResponse is returned.

    :param user (AddUserModel): An instance of AddUserModel that includes username, password ,user_type,email and
    address
    :return JSONResponse:  A JSON response that contains status code 200 and content which contains user_id,
    username, user_type and access_token if credentials is valid.
    :raise HTTPException:If the registration fails due to validation errors
        or if the user already exists HTTPException is raised.This includes status code and message.
    """
    user_exist=await users_collection.find_one({"username":user.username,"is_deleted":False})
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    hash_p=hash_password.create_password_hash(user.password)
    user.password=hash_p
    insert_user={
        "username" :user.username,
    "password" : user.password,
    "user_type" : user.user_type,
        "address":user.address,
        "email":user.email,
        "is_deleted": False
    }
    inserted_user=await users_collection.insert_one(insert_user)
    access_token = create_access_token(user={"sub": user.username})
    response_model=LoginResponseModel(
        id=str(inserted_user.inserted_id),
        username=user.username,
        user_type=user.user_type,
        access_token=access_token
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=jsonable_encoder(response_model))


@auth_router.delete("/members/delete-my-account")
async def delete_my_account(user: object = Depends(authenticate)) -> JSONResponse:
    """
    Method allows members to delete their account
    :param user:  An authenticated user object retrieved  through dependency injection.
    :return JSONResponse:  A JSON response that contains status code 200 and content which contains success message.
    :raise HTTPException:
    - 403 forbidden :   If user is librarian

    """
    if user.get("user_type") != UserType.member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    await users_collection.update_one({"_id": ObjectId(user.get("_id"))}, {"$set": {"is_deleted": True}})
    response = {
        "message": "Account deleted successfully"
    }
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=response)








