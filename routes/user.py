from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from pydantic import BaseModel
from passlib.context import CryptContext
from settings import settings
from database import get_session
from models import User

router = APIRouter(
    prefix="/admin/users",
    tags=["admin"],
    responses={404: {"description": "Not found"}}
)

SECRET_KEY = settings['SECRET_KEY']
ALGORITHM = settings['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = settings['ACCESS_TOKEN_EXPIRE_MINUTES']


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_username(username: str) -> User:
    with Session(get_session()) as session:
        return session.exec(select(User).where(User.username == username)).first()


def get_authenticated_user(
        username: str, 
        password: str, 
        session: Session = Depends(get_session)
    ) -> User:
    print(username, password)
    user = get_user_by_username(username, session)
    print(user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, session=Depends(get_session))
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



@router.get("/", response_model=list[User])
async def get_users(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    users = await session.exec(select(User)).scalars().all()
    return [User(id=user.id, name=user.username, code=user.email) for user in users]


@router.post("/", response_model=User)
async def create_User(
        user: User, 
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    user_exist = session.exec(select(User).where(User.username == user.username)).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        username=user.username,
        email=user.email,
        name=user.name,
        password=get_password_hash(user.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/{user_id}", response_model=User)
async def get_User(
        user_id: int, 
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    user = await session.get(User, user_id)
    if not User:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}")
async def update_User(
        user_id: int, 
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    return {"User": user_id}


@router.delete("/{user_id}")
async def delete_User(
        user_id: int, 
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    return {"User": user_id}



