from bson import ObjectId
from fastapi import Depends, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from api.auth.authenticate import authenticate
from api.auth.hash_password import HashPassword
from api.database.connection import users_collection, books_collection
from api.model.base import PyObjectId
from api.model.book import Books
from api.model.user import UserType, Users, UpdateMemberBody, AddUserModel

member_router = APIRouter(
    tags=['Members'],
    responses={404: {
        "description": "Not found"
    }},
)

hash_password = HashPassword()



@member_router.get("/members")
async def get_members_list(user: object = Depends(authenticate)) -> dict:
    """
    This endpoint will return list of members exist in system.
    :param user:  An authenticated user object retrieved  through dependency injection.
    :return (dict): A dict that contains list of members
    :raise HTTPException:
    - 403 forbidden :   If user is member

    """
    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    members = await users_collection.find({"user_type": UserType.member}).to_list(None)
    members = [Users(**x).list_members() for x in members]
    response = {
        "members": members
    }
    return response


@member_router.post("/members")
async def create_member(user_request: AddUserModel, user: object = Depends(authenticate)) -> JSONResponse:
    """
    This endpoint allow librarian to create a new members to the system.
    :param user_request: An instance of AddUserModel that includes username, password ,user_type,email and
    address
    :param user:  An authenticated user object retrieved  through dependency injection.
    :return JSONResponse:  A JSON response that contains status code 201 and content which contains success message.
    :raise HTTPException:
    - 403 forbidden :   If user is member
    - 400 Bad request : If username already exist
    """
    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    user_exist = await users_collection.find_one({"username": user_request.username, "is_deleted": False})
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exist",

        )
    hash_p = hash_password.create_password_hash(user_request.password)
    user_request.password = hash_p
    insert_user = {
        "username": user_request.username,
        "password": user_request.password,
        "user_type": user_request.user_type,
    "address":user_request.address,
        "email":user_request.email,
        "is_deleted": False
    }
    await users_collection.insert_one(insert_user)
    response = {
        "message": "Member added successfully"
    }
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=response)


@member_router.put("/members/{member_id}")
async def update_member(member_id: PyObjectId, user_request: UpdateMemberBody,
                        user: object = Depends(authenticate)) -> JSONResponse:
    """
    This endpoint allow librarian to update members exist in the system
    :param member_id (PyObjectId): The unique identifier of the member to be updated.
    :param user_request: An instance of AddUserModel that includes username, password ,user_type,email and
    address
    :param user:  An authenticated user object retrieved  through dependency injection.
    :return JSONResponse:  A JSON response that contains status code 200 and content which contains success message.
    :raise HTTPException:
    - 403 forbidden :   If user is member
    - 400 Bad request : If username already exist
    - 404 Not found : If member not found
    """
    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    member = await users_collection.find_one({"_id": member_id, "is_deleted": False})
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",

        )
    if member.get("username") != user_request.username:
        user_exist = await users_collection.find_one({"username": user_request.username,
                                                      "is_deleted": False})
        if user_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username already exist",

            )
    await users_collection.update_one({"_id": ObjectId(member_id)}, {"$set": user_request.__dict__})
    response = {
        "message": "Member updated successfully"
    }
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=response)


@member_router.delete("/members/{member_id}")
async def delete_member(member_id: PyObjectId, user: object = Depends(authenticate)) -> JSONResponse:
    """
    This endpoint allow librarian to remove members.
    :param member_id (PyObjectId): The unique identifier of the member to be removed.
    :param user:  An authenticated user object retrieved  through dependency injection.
    :return JSONResponse:  A JSON response that contains status code 200 and content which contains success message.
    :raise HTTPException:
    - 403 forbidden :   If user is member
    - 404 Not found : If member not found
    """
    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    member = await users_collection.find_one({"_id": ObjectId(member_id), "is_deleted": False})
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",

        )
    await users_collection.update_one({"_id": ObjectId(member_id)}, {"$set": {"is_deleted": True}})
    response = {
        "message": "Member deleted successfully"
    }
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=response)


@member_router.get("/members/{member_id}/history")
async def get_history(member_id: PyObjectId, user: object = Depends(authenticate)) -> dict:
    """
    This endpoint allow to get history of book borrowed and returned by specified member
   :param member_id (PyObjectId): The unique identifier of the member.
    :param user:  An authenticated user object retrieved  through dependency injection.
    :return (dict): A dict that contains list of books.
      :raise HTTPException:
    - 403 forbidden :   If user is member
    - 404 Not found : If member not found
    """
    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    member = await users_collection.find_one({"_id": member_id, "is_deleted": False})
    if member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",

        )
    books = await books_collection.find({"borrowed_by_id": ObjectId(member_id)}).to_list(None)
    books = [Books(**x).list_books() for x in books]
    response = {
        "books": books
    }
    return response


@member_router.get("/members/{member_id}")
async def get_member_by_id(member_id: PyObjectId, user: object = Depends(authenticate)) -> dict:
    """
    This endpoint will return specified member by its id
   :param member_id (PyObjectId): The unique identifier of the member.
    :param user:  An authenticated user object retrieved  through dependency injection.
    :return (dict): A dict that contains list of books.
      :raise HTTPException:
    - 403 forbidden :   If user is member
    - 404 Not found : If member not found
    """
    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    member = await users_collection.find_one({"_id": ObjectId(member_id), "is_deleted": False})
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    member_inst = Users(**member).detailed_response()
    response = {
        "member": member_inst
    }
    return response



