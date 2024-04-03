from fastapi import FastAPI, APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from routes.country import router as country_router
from routes.user import router as user_router
from contextlib import asynccontextmanager
from populate.first_user import create_first_user
from database import get_session
from models import User
from security import (oauth2_scheme, Token, TokenData, get_authenticated_user,
                      ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, 
                      get_current_active_user)



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_first_user()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(country_router)


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = get_authenticated_user(
        form_data.username, 
        form_data.password, 
        session = Depends(get_session())
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/checkdb")
async def check_db(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return [user.username for user in users]
