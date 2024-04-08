from typing import Annotated
from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from routes.country import router as country_router
from routes.user import router as user_router
from routes.currency import router as currency_router
from routes.bank import router as bank_router
from routes.project import router as project_router
from contextlib import asynccontextmanager
from populate.first_user import create_first_user
from models import User, UserBase, UserRead
from security import (Token, get_authenticated_user,
                      create_user_access_token,
                      get_current_active_user,
                      get_current_super_user)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_first_user()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(country_router)
app.include_router(currency_router)
app.include_router(bank_router)
app.include_router(project_router)


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
    scopes = form_data.scopes
    if user.is_superuser and not "superuser" in form_data.scopes:
        scopes.append("superuser")
    elif not "me" in form_data.scopes:
        scopes.append("me")
    access_token = create_user_access_token(
                     data = {"sub": user.username,
                             "scopes": scopes}
                   )
    return Token(access_token=access_token, token_type="bearer")



