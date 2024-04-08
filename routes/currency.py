
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Currency, CurrencyBase, User
from security import (oauth2_scheme,
                      get_current_active_user,
                      get_current_super_user)


router = APIRouter(
    prefix="/currencies",
    tags=["currencies"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=list[Currency])
async def get_currencies(
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    currencies = session.exec(select(Currency)).all()
    return currencies


@router.post("/", response_model=Currency)
async def create_currency(
            currency: CurrencyBase,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    statement = select(Currency).where(Currency.name == currency.name)
    currency_exist = session.exec(statement).first()
    if currency_exist:
        raise HTTPException(status_code=400, detail="Currency already exists")
    currency = Currency(name=currency.name, code=currency.code)
    session.add(currency)
    session.commit()
    session.refresh(currency)
    return currency


@router.get("/{currency_id}", response_model=Currency)
async def get_currency(
            currency_id: int,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    currency = session.get(Currency, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency


@router.patch("/{currency_id}")
async def update_currency(
            currency_id: int,
            currency: CurrencyBase,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    db_currency = session.get(Currency, currency_id)
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    currency_data = currency.model_dump(exclude_unset=True)
    for key, value in currency_data.items():
        setattr(db_currency, key, value)
    session.add(db_currency)
    session.commit()
    session.refresh(db_currency)
    return db_currency


@router.delete("/{currency_id}")
async def delete_currency(
            currency_id: int,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    currency = session.get(Currency, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="currency not found")
    session.delete(currency)
    session.commit()
    return {"ok": True}


@router.get("/admin/populate")
async def populate_initial_currencies(
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_super_user)],
            session: Session = Depends(get_session)
          ):
    from populate.currencies import populate_currencies
    currencies = session.exec(select(Currency)).all()
    if not currencies:
        populate_currencies()
        return {"message": "Currencies populated"}
    else:
        return {"message": "Currencies already populated"}
