import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.usermodel import User
from . import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = config.secret_key
ALGORITHM = config.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.access_token_expire_minutes


class TokenData:
    def __init__(self, username: str, user_id: int):
        self.username = str(username)
        self.user_id = int(user_id)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_expection):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("username")
        user_id: int = payload.get("user_id")

        if username is None or user_id is None:
            raise credentials_expection
        token_data = TokenData(username=username, user_id=user_id)
        return token_data

    except InvalidTokenError:
        raise credentials_expection


def get_current_user(session: Session, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)

    user = (
        session.query(User)
        .filter(User.username == token_data.username)
        .filter(User.id == token_data.user_id)
        .first()
    )
    if user is None:
        raise credentials_exception
    return user
