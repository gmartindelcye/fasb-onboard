
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Country, CountryBase, User
from security import (oauth2_scheme,
                      get_current_active_user,
                      get_current_super_user)


router = APIRouter(
    prefix="/countries",
    tags=["countries"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=list[Country])
async def get_countries(
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    countries = session.exec(select(Country)).all()
    return countries


@router.post("/", response_model=Country)
async def create_country(
            country: CountryBase,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    statement = select(Country).where(Country.name == country.name)
    country_exist = session.exec(statement).first()
    if country_exist:
        raise HTTPException(status_code=400, detail="Country already exists")
    country = Country(name=country.name, code=country.code)
    session.add(country)
    session.commit()
    session.refresh(country)
    return country


@router.get("/{country_id}", response_model=Country)
async def get_country(
            country_id: int,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    country = session.get(Country, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.patch("/{country_id}")
async def update_country(
            country_id: int,
            country: CountryBase,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    db_country = session.get(Country, country_id)
    if not db_country:
        raise HTTPException(status_code=404, detail="Country not found")
    country_data = country.model_dump(exclude_unset=True)
    for key, value in country_data.items():
        setattr(db_country, key, value)
    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country


@router.delete("/{country_id}")
async def delete_country(
            country_id: int,
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_active_user)],
            session: Session = Depends(get_session)
          ):
    country = session.get(Country, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="country not found")
    session.delete(country)
    session.commit()
    return {"ok": True}


@router.get("/admin/populate")
async def populate_initial_countries(
            token: Annotated[str, Depends(oauth2_scheme)],
            current_user: Annotated[
                            User,
                            Depends(get_current_super_user)],
            session: Session = Depends(get_session)
          ):
    from populate.countries import populate_countries
    countries = session.exec(select(Country)).all()
    if not countries:
        populate_countries()
        return {"message": "Countries populated"}
    else:
        return {"message": "Countries already populated"}
