from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from routes.country import router as country_router
from routes.user import router as user_router
from routes.currency import router as currency_router
from contextlib import asynccontextmanager
from populate.first_user import create_first_user
from models import User
from security import (Token, get_authenticated_user,
                      create_user_access_token,
                      get_current_active_user)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_first_user()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(country_router)
app.include_router(currency_router)


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.post("/token", response_model=Token)
async def login_for_access_token(
            form_data: OAuth2PasswordRequestForm = Depends()
          ) -> Token:
    user = get_authenticated_user(
        form_data.username,
        form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_user_access_token(user.username)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
