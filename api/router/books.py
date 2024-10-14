from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Body
from starlette import status
from starlette.responses import JSONResponse

from api.auth.authenticate import authenticate
from api.database.connection import books_collection, book_logs_collection
from api.model.base import PyObjectId
from api.model.book import BooksRequestBody, Books, BookStatus
from api.model.user import UserType
from api.utils.utils import get_timestamp

book_router = APIRouter(
    tags=['Books'],
    responses={404: {
        "description": "Not found"
    }},
)

@book_router.post("/books")
async def create_book(book:BooksRequestBody=Body(...),user:object=Depends(authenticate))->JSONResponse:
    """
    This endpoint allow librarian user to add new book entry into system.
    :param book (BooksRequestBody): An instance of BooksRequestBody that includes book_name , description,
    author, genre
    :param user (object):  An authenticated user object retrieved  through dependency injection.
    :return JSONResponse:  A JSON response that contains status code 200 and content which contains success message
     :raise HTTPException: If user is member HTTPException (403) is raised.This includes status code and message.
    """
    if user.get("user_type")!=UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    insert_book={
        "name":book.name,
        "description":book.description,
        "created_ts":get_timestamp(),
        "author":book.author,
        "genre":book.genre,
        "is_deleted":False
    }
    await books_collection.insert_one(insert_book)
    response={
           "message":"Book added successfully"
       }
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                           content=response)


@book_router.get("/books")
async def get_all_books(user:object=Depends(authenticate))->dict:
    """
    This endpoint list down all books available in the system
    :param user:  An authenticated user object retrieved  through dependency injection.
    :return (dict): A dict that contains list of books
    """
    books= await books_collection.find({"is_deleted":False}).to_list(None)
    books=[Books(**x).list_books() for x in books]
    response={
        "books":books
    }
    return response


@book_router.put("/books/{book_id}")
async def update_book(book_id:PyObjectId,book_request:BooksRequestBody,user:object=Depends(authenticate))->JSONResponse:
    """
    This endpoint allow librarian to update book that available in the system.
    :param book_id (PyObjectId): The unique identifier of the book to be updated.
    param book_request:  An instance of BooksRequestBody that includes book_name , description,
    author, genre
    :param user (object):  An authenticated user object retrieved  through dependency injection.
    :return JSONResponse:  A JSON response that contains status code 200 and content which contains success message.
    :raise HTTPException:
    - 403 forbidden :   If user is member
    - 404 not found : If book with specified id doesn't exist
    """
    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    book= await books_collection.find_one({"_id":ObjectId(book_id)})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    query={
        "_id":ObjectId(book_id)
    }
    await books_collection.update_one(query,{"$set":book_request.__dict__})
    response={
        "message":"Updated successfully"
    }
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=response)

@book_router.get("/books/{book_id}")
async def get_book_by_id(book_id:PyObjectId,user:object=Depends(authenticate))->JSONResponse:
    """
    This endpoint retrieve specified book by its ID
    :param book_id (PyObjectId): The unique identifier of the book.
    :param user (object):  An authenticated user object retrieved  through dependency injection.
    :return JSONResponse:  A JSON response that contains status code 200 and content which contains success message.
    :raise HTTPException:
    - 403 forbidden :   If user is member
    - 404 not found : If book with specified id doesn't exist
    """
    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    book= await books_collection.find_one({"_id":ObjectId(book_id)})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    book=Books(**book).detailed_response()
    response={
        "book":book
    }
    return response

@book_router.delete("/books/{book_id}")
async def remove_book(book_id:PyObjectId,user:object=Depends(authenticate))->JSONResponse:
    """
    This endpoint allow librarian to remove existing book
   :param book_id (PyObjectId): The unique identifier of the book.
    :param user (object):  An authenticated user object retrieved  through dependency injection.
    :return JSONResponse:  A JSON response that contains status code 200 and content which contains success message.
    :raise HTTPException:
    - 403 forbidden :   If user is member
    - 404 not found : If book with specified id doesn't exist
    """

    if user.get("user_type") != UserType.librarian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    book= await books_collection.find_one({"_id":ObjectId(book_id),"is_deleted":False})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    query = {
        "_id": ObjectId(book_id)
    }
    await books_collection.update_one(query, {"$set":{"is_deleted":True} })
    response = {
        "message": "Deleted successfully"
    }
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=response)

@book_router.post("/books/{book_id}/borrow-return/{borrow_status}")
async def borrow_return_book(book_id:PyObjectId,borrow_status:bool,user:object=Depends(authenticate))->JSONResponse:
    """
    This endpoint allow members to borrow or return existing books
   :param book_id (PyObjectId): The unique identifier of the book.
    :param user (object):  An authenticated user object retrieved  through dependency injection.
    :param borrow_status (bool): A boolean value that represent the action to be performed.
    - True: if member is borrowing book
    - False : if member is returning book
     :return JSONResponse:  A JSON response that contains status code 201 and content which contains success message.
    :raise HTTPException:
    - 403 forbidden :   If user is librarian
    - 404 not found : If book with specified id doesn't exist
    """
    if user.get("user_type") != UserType.member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to perform this action.",

        )
    book = await books_collection.find_one({"_id": ObjectId(book_id), "is_deleted": False})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    query = {
        "_id": ObjectId(book_id)
    }
    update_borrow_details={

        "borrowed_by_id":ObjectId(user.get("_id")),
        "borrowed_by_name":user.get("username")

    }
    if borrow_status:
        book_status = BookStatus.borrowed
        update_borrow_details["borrowed_ts"]=get_timestamp()
        update_borrow_details["returned_ts"] =0
        update_borrow_details["status"]=BookStatus.borrowed
    else:
        update_borrow_details["returned_ts"] = get_timestamp()
        update_borrow_details["status"] = BookStatus.available
        book_status = BookStatus.available
    await books_collection.update_one(query, {"$set": update_borrow_details})

    response = {
        "message": f"{book_status.value.capitalize() if book_status.value==BookStatus.borrowed else 'Returned'} successfully"
    }
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=response)


