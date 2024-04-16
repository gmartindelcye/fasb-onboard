from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from routes.user import router as user_router
from routes.country import router as country_router
from routes.currency import router as currency_router
from routes.bank import router as bank_router
from routes.project import router as project_router
from routes.account import router as account_router
from routes.partner import router as partner_router
from contextlib import asynccontextmanager
from populate.first_user import create_first_user
from security import (
    Token,
    get_authenticated_user,
    create_user_access_token,
)
from settings import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
)

origins = [
    "http://localhost",
    "http://localhost:3000",
]



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_first_user()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(country_router)
app.include_router(currency_router)
app.include_router(bank_router)
app.include_router(project_router)
app.include_router(account_router)
app.include_router(partner_router)


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
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
    if user.is_superuser and "superuser" not in form_data.scopes:
        scopes.append("superuser")
    elif "me" not in form_data.scopes:
        scopes.append("me")
    access_token = create_user_access_token(
        data={"sub": user.username, "scopes": scopes}
    )
    return Token(access_token=access_token, token_type="bearer")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://portal.phalkons.com/assets/logo-dae52d9a.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
