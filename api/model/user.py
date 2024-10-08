from enum import Enum

from pydantic import BaseModel, Field, EmailStr

from api.model.base import PyObjectId


class UserType(str,Enum):
    librarian="librarian"
    member="member"

class AddUserModel(BaseModel):
    username: str
    password: str
    user_type: UserType
    address:str
    email:EmailStr

    class Config:
        schema_extra = {
            "example": {
                "username": "jdoe",
                "password": "Testtest1#",
                "user_type": "librarian",
                "address":"street rd",
                "email":"jdoe@example.com"
            }
        }


class Users(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username:str
    password:str
    user_type:UserType
    address: str
    email: EmailStr
    is_deleted:bool=False

    class Config:
        schema_extra={
            "example": {
                "username": "jdoe",
                "password":"Testtest1#",
                "user_type":"librarian"
            }
        }
    def list_members(self):
        return {
            "id":str(self.id),
            "username":self.username,
            "address":self.address,
            "email":self.email,
            "status":"Active" if not self.is_deleted else "Deleted"
        }

    def detailed_response(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "user_type": self.user_type,
            "address": self.address,
            "email": self.email,
        }


class LoginResponseModel(BaseModel):
    id: str
    username: str
    user_type: str
    access_token: str

class UpdateMemberBody(BaseModel):
    username:str
    user_type:str


    class config:
        schema_extra={
            "example": {
                "username": "jdoe",

                "user_type":"member"
            }
        }

