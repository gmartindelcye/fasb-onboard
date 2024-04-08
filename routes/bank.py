
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Bank, BankBase, User
from security import oauth2_scheme, get_current_active_user


router = APIRouter(
    prefix="/banks",
    tags=["banks"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=list[Bank])
async def get_banks(
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    banks = session.exec(select(Bank)).all()
    return banks


@router.post("/", response_model=Bank)
async def create_bank(
            bank: BankBase,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    statement = select(Bank).where(Bank.name == bank.name)
    bank_exist = session.exec(statement).first()
    if bank_exist:
        raise HTTPException(status_code=400, detail="Bank already exists")
    bank = Bank(name=bank.name, code=bank.code)
    session.add(bank)
    session.commit()
    session.refresh(bank)
    return bank


@router.get("/{bank_id}", response_model=Bank)
async def get_bank(
            bank_id: int,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    bank = session.get(Bank, bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    return bank


@router.patch("/{bank_id}")
async def update_bank(
            bank_id: int,
            bank: BankBase,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    db_bank = session.get(Bank, bank_id)
    if not db_bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    bank_data = bank.model_dump(exclude_unset=True)
    for key, value in bank_data.items():
        setattr(db_bank, key, value)
    session.add(db_bank)
    session.commit()
    session.refresh(db_bank)
    return db_bank


@router.delete("/{bank_id}")
async def delete_bank(
            bank_id: int,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    bank = session.get(Bank, bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="bank not found")
    session.delete(bank)
    session.commit()
    return {"ok": True}
