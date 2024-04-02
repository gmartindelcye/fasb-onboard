
from typing import Optional, List, Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import User
from utils import get_password_hash
from security import oauth2_scheme

router = APIRouter(
    prefix="/admin/users",
    tags=["admin"],
    responses={404: {"description": "Not found"}}
)


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



