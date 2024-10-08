from enum import Enum
from typing import Optional



from pydantic import BaseModel, Field

from api.model.base import PyObjectId


class BooksRequestBody(BaseModel):
    name:str
    description:str
    author:str
    genre:str

    class Config:
        schema_extra = {
            "example": {
                "name": "Angels & demons",
                "description": "Fiction books",
                "author":"Dan brown",
                "genre":"Fiction"
            }
        }

class BookStatus(str,Enum):
    borrowed="BORROWED"
    available="AVAILABLE"
class Books(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name:str
    description:str
    author: str
    genre: str
    status:str=BookStatus.available
    created_ts:int
    returned_ts: Optional[int] = 0
    borrowed_ts: Optional[int] = 0
    borrowed_by_id: Optional[PyObjectId] = None
    borrowed_by_name:Optional[str]=""
    is_deleted:bool=False

    class Config:
        schema_extra = {
            "example": {
                "name": "jdoe",
                "description": "test"
            }
        }


    def list_books(self):
        return {
            "id":str(self.id),
            "name":self.name,
            "author":self.author,
            "genre":self.genre,
            "status":self.status,
            "borrowed_by": self.borrowed_by_name,
            "borrow_by_id":str(self.borrowed_by_id),
            "borrowed_ts": self.borrowed_ts,
            "returned_ts": self.returned_ts
        }

    def detailed_response(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description":self.description,
            "author": self.author,
            "genre": self.genre,
        }







