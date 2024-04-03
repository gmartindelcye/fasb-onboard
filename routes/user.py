from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from database import get_session
from models import (User, UserBase, UserRead, UserCreate, UserPassword,
                    UserActive, UserSuperuser)
from security import oauth2_scheme, get_password_hash

router = APIRouter(
    prefix="/admin/users",
    tags=["admin"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=list[UserRead])
async def get_users(
            token: Annotated[str, Depends(oauth2_scheme)],
            session: Session = Depends(get_session)
          ):
    users = session.exec(select(User)).all()
    return users


@router.post("/", response_model=UserRead)
async def create_User(
            user: UserCreate,
            token: Annotated[str, Depends(oauth2_scheme)],
            session: Session = Depends(get_session)
          ):
    statement = select(User).where(User.username == user.username)
    user_exist = session.exec(statement).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        username=user.username,
        email=user.email,
        name=user.name,
        password=get_password_hash(user.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{user_id}", response_model=User)
async def get_User(
            user_id: int,
            token: Annotated[str, Depends(oauth2_scheme)],
            session: Session = Depends(get_session)
          ):
    user = session.get(User, user_id)
    if not User:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_User(
            user_id: int,
            user: UserBase,
            token: Annotated[str, Depends(oauth2_scheme)],
            session: Session = Depends(get_session)
          ):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_User(
            user_id: int,
            token: Annotated[str, Depends(oauth2_scheme)],
            session: Session = Depends(get_session)
          ):
    user = session.get(User, user_id)
    if not User:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.post("/password/{user_id}")
def change_password(
      user_id: int,
      password: UserPassword,
      token: Annotated[str, Depends(oauth2_scheme)],
      session: Session = Depends(get_session)
     ):
    user = session.get(User, user_id)
    if not User:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = get_password_hash(password.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"ok": True}


@router.post("/active/{user_id}")
def change_active(
      user_id: int,
      active: UserActive,
      token: Annotated[str, Depends(oauth2_scheme)],
      session: Session = Depends(get_session)
     ):
    user = session.get(User, user_id)
    if not User:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = active.is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"ok": True}


@router.post("/superuser/{user_id}")
def change_superuser(
      user_id: int,
      superuser: UserSuperuser,
      token: Annotated[str, Depends(oauth2_scheme)],
      session: Session = Depends(get_session)
     ):
    user = session.get(User, user_id)
    if not User:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_superuser = superuser.is_superuser
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"ok": True}
