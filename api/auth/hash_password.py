from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashPassword:

    def verify_password(self,plain_password:str, hashed_password:str):
        return pwd_context.verify(plain_password, hashed_password)

    def create_password_hash(self,password:str):
        return pwd_context.hash(password)

