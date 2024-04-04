from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field


class BankBase(SQLModel):
    name: str = Field(default=None, unique=True, index=True)
    code: str | None = Field(default=None, unique=True, index=True)


class Bank(BankBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CountryBase(SQLModel):
    name: str = Field(default=None, unique=True, index=True)
    code: str | None = Field(default=None, unique=True, index=True)


class Country(CountryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# class CountryRead(Country):
#     pass

class CurrencyBase(SQLModel):
    name: str = Field(default=None, unique=True, index=True)
    code: str | None = Field(default=None, unique=True, index=True)


class Currency(CurrencyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)



class UserBase(SQLModel):
    username: str = Field(default=None, unique=True, index=True)
    name: str | None = Field(default=None)
    email: str | None = Field(default=None, unique=True, index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: Optional[str] = Field(default=None)
    token: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    # projects: list["Project"] = Relationship(back_populates="owner")


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    password: str


class UserPassword(SQLModel):
    password: str


class UserActive(SQLModel):
    is_active: bool = Field(default=True)


class UserSuperuser(SQLModel):
    is_superuser: bool = Field(default=False)


# class Project(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(default=None, unique=True, index=True)
#     description: Optional[str] = Field(default=None)
#     owner_id: int = Field(default=None, foreign_key="user.id")
#     owner: User = Relationship(back_populates="projects")
#     tree: Optional[str] = Field(default=None)
#     accounts: list["Account"] = Relationship(back_populates="project")


# class Partner(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(default=None, unique=True, index=True)
#     description: Optional[str] = Field(default=None)
#     percentage: Decimal = Field(
#                                 default=Decimal(0.0),
#                                 max_digits=6,
#                                 decimal_places=2
#                           )
#     account_id: int = Field(default=None, foreign_key="account.id")
#     account: "Account" = Relationship(back_populates="partners")


# class Account(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(default=None, unique=True, index=True)
#     description: Optional[str] = Field(default=None)
#     initial_date: datetime | None = Field(default=None)
#     account_number: str = Field(default=None, unique=True, index=True)
#     alias: str = Field(default=None)
#     project_id: int = Field(default=None, foreign_key="project.id")
#     project: Project = Relationship(back_populates="accounts")
#     bank_id: int = Field(default=None, foreign_key="bank.id")
#     bank: Bank = Relationship(back_populates="accounts")
#     currency_id: int = Field(default=None, foreign_key="currency.id")
#     currency: Currency = Relationship(back_populates="accounts")
#     country_id: int = Field(default=None, foreign_key="country.id")
#     country: Country = Relationship(back_populates="accounts")
#     partners: list[Partner] = Relationship(back_populates="partners")
