from passlib.context import CryptContext 
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException


from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict):
 
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
 
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

from jose import JWTError
# import bearer authentication reads the authorization header (authorization Bearer ejdi.....)
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
# http auth cred stores the token sent by the user 


# create bearer object , as it automatically extracts (Bearer eyhdi...)

security = HTTPBearer()

# function  to verify the jwt roken received in the authorization header 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return email

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )