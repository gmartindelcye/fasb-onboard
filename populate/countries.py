from sqlmodel import Session
from models import Country
from database import engine
from .countries_data import COUNTRIES


def populate_countries():
    with Session(engine) as session:
        for key, value in COUNTRIES.items():
            country = Country(name=value, code=key)
            session.add(country)
        session.commit()

        return {"message": "Countries Data populated"}
