from sqlmodel import Session
from models import Currency
from database import engine
from .currencies_data import CURRENCIES


def populate_currencies():
    with Session(engine) as session:
        for key, value in CURRENCIES.items():
            currency = Currency(name=value, code=key)
            session.add(currency)
        session.commit()

        return {"message": "Currencies Data populated"}
