from typing import Optional, Annotated
from datetime import datetime

from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship


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
    projects: Optional[list["Project"]] = Relationship(back_populates="owner")


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


class ProjectBase(SQLModel):
    name: str = Field(default=None, unique=True, index=True)
    description: Optional[str] = Field(default=None)


class Project(ProjectBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    creation_date: datetime = Field(default=datetime.now())
    tree: Optional[str] = Field(default="")
    owner_id: int = Field(default=None, foreign_key="user.id")
    owner: User = Relationship(back_populates="projects")
    accounts: Optional[list["Account"]] = Relationship(
        back_populates="project"
    )


class PartnerBase(SQLModel):
    name: str = Field(default=None, unique=True, index=True)
    description: Optional[str] = Field(default=None)
    percentage: Decimal = Field(
                                default=Decimal(0.0),
                                max_digits=5,
                                decimal_places=2
                          )


class PartnerCreate(PartnerBase):
    account_id: int = Field(default=None, foreign_key="account.id")



class Partner(PartnerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(default=None, foreign_key="account.id")
    account: "Account" = Relationship(back_populates="partners")


class AccountBase(SQLModel):
    name: str = Field(default=None, unique=True, index=True)
    description: Optional[str] = Field(default=None)
    initial_date: datetime | None = Field(default=None)
    account_number: str = Field(default=None, unique=True, index=True)
    alias: str = Field(default=None)
    amount: Annotated[Decimal, Field(
                                default=0,
                                max_digits=12,
                                decimal_places=2
                          )]


class AccountCreate(AccountBase):
    project_id: int
    bank_id: int
    currency_id: int
    country_id: int


class Account(AccountBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    project: Project = Relationship(back_populates="accounts")
    bank_id: int = Field(foreign_key="bank.id")
    bank: Bank = Relationship()
    currency_id: int = Field(foreign_key="currency.id")
    currency: Currency = Relationship()
    country_id: int = Field(foreign_key="country.id")
    country: Country = Relationship()
    partners: Optional[list["Partner"]] = Relationship(back_populates="account")
