from fastapi import FastAPI
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from api.router import auth, books, members

app=FastAPI()

origins = [
    "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.auth_router)
app.include_router(books.book_router)
app.include_router(members.member_router)

if __name__ == '__main__':
    uvicorn.run(app=app, host='localhost', port=8000)