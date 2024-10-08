from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, Depends
from starlette import status

from api.database.connection import Settings
from jose import jwt, JWTError
setting=Settings()

def create_access_token(user: dict):
    expires_delta = timedelta(minutes=45)
    to_encode = user.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, setting.secret_key, algorithm=setting.algorithm)
    return encoded_jwt


def verify_access_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, setting.secret_key, algorithms=[setting.algorithm])
        username= str(payload.get("sub"))
        expire=float(payload.get("exp"))
        if username is None or expire is None:
            raise credentials_exception
        if datetime.utcnow().timestamp()> expire:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception