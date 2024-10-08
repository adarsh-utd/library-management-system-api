import os
from typing import Optional, Any

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.v1 import BaseSettings


MONGODB_URL = os.getenv("database_url")
DB_NAME = os.getenv("database_name")
client =AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

users_collection = db["users"]
books_collection =db["books"]
book_logs_collection=db["book_logs"]

class Settings(BaseSettings):
    secret_key:Optional[str]=None
    algorithm:Optional[str]=None

    class config:
        env_file=".env"






