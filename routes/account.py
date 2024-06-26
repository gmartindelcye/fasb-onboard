from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Account, AccountBase, AccountCreate, User, Project
from security import oauth2_scheme, get_current_active_user


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}},
)


def verify_project_user(
    project_id: int, user_id: int, session: Session
) -> bool:
    statement = select(Project).filter(Project.id == project_id)
    project = session.exec(statement).first()
    owner = project.owner
    if project.id == project_id and owner.id == user_id:
        return False
    return True


def verify_account_project_user(
    account_id: int, project_id: int, user_id: int, session: Session
) -> bool:
    statement = select(Account).filter(Account.id == account_id)
    account = session.exec(statement).first()
    project = account.project
    owner = project.owner
    if (
        account.id == account_id
        and project.id == project_id
        and owner.id == user_id
    ):
        return False
    return True


@router.get("/{project_id}", response_model=list[Account])
async def get_accounts(
    project_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(Account.project_id == project_id)

    if not current_user.is_superuser:
        if verify_project_user(project_id, current_user.id, session):
            raise HTTPException(status_code=403, detail="Not allowed")

    accounts = session.exec(statement).all()
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    return accounts


@router.post("/{project_id}", response_model=Account)
async def create_account(
    project_id: int,
    account: AccountCreate,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if not current_user.is_superuser:
        if verify_project_user(project_id, current_user.id, session):
            raise HTTPException(status_code=403, detail="Not allowed")
    statement = select(Account).filter(Account.name == account.name)
    account_exist = session.exec(statement).first()
    if account_exist:
        raise HTTPException(status_code=400, detail="Account already exists")
    account = Account(
        name=account.name,
        description=account.description,
        initial_date=account.initial_date,
        account_number=account.account_number,
        alias=account.alias,
        amount=account.amount,
        bank_id=account.bank_id,
        currency_id=account.currency_id,
        country_id=account.country_id,
        project_id=project_id,
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.get("/{project_id}/{account_id}", response_model=Account)
async def get_account(
    project_id: int,
    account_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(
        Account.id == account_id, Account.project_id == project_id
    )
    if not current_user.is_superuser:
        if verify_account_project_user(
            account_id, project_id, current_user.id, session
        ):
            raise HTTPException(status_code=403, detail="Not allowed")
    account = session.exec(statement).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch("/{project_id}/{account_id}")
async def update_account(
    project_id: int,
    account_id: int,
    account: AccountBase,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(
        Account.id == account_id, Account.project_id == project_id
    )
    if not current_user.is_superuser:
        if verify_account_project_user(
            account_id, project_id, current_user.id, session
        ):
            raise HTTPException(status_code=403, detail="Not allowed")
    db_account = session.exec(statement).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    account_data = account.model_dump(exclude_unset=True)
    for key, value in account_data.items():
        setattr(db_account, key, value)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@router.delete("/{project_id}/{account_id}")
async def delete_account(
    project_id: int,
    account_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(
        Account.id == account_id, Account.project_id == project_id
    )
    if not current_user.is_superuser:
        if verify_account_project_user(
            account_id, project_id, current_user.id, session
        ):
            raise HTTPException(status_code=403, detail="Not allowed")
    account = session.exec(statement).first()
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    session.delete(account)
    session.commit()
    return {"ok": True}
