from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel import Session, select
from pydantic import BaseModel, ValidationError
from passlib.context import CryptContext
from settings import settings
from database import engine
from models import User
from jose import jwt, JWTError

SECRET_KEY = settings['SECRET_KEY']
ALGORITHM = settings['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = settings['ACCESS_TOKEN_EXPIRE_MINUTES']
ATEM = ACCESS_TOKEN_EXPIRE_MINUTES


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "superuser": "Read and write information from all users.",
        "me": "Read information from the current user.",
    }
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str) -> User:
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()


def get_authenticated_user(
        username: str,
        password: str,
      ) -> User:
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(
      data: dict,
      expires_delta: timedelta | None = None
      ) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ATEM)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_user_access_token(data: dict) -> str:
    access_token_expires = timedelta(minutes=int(ATEM))
    access_token = create_access_token(
        data=data, expires_delta=access_token_expires
    )
    return access_token


def get_current_user(
      security_scopes: SecurityScopes,
      token: Annotated[str, Depends(oauth2_scheme)]
      ):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
            current_user: Annotated[
                            User,
                            Security(get_current_user, scopes=["me"])],
          ):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_super_user(
            current_user: Annotated[
                            User,
                            Security(get_current_user, scopes=["superuser"])],
          ):
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not superuser")
    return current_user
