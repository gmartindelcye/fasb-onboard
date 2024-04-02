
from typing import Optional, List, Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Country
from security import oauth2_scheme


router = APIRouter(
    prefix="/countries",
    tags=["countries"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=list[Country])
async def get_countries(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    countries = await session.exec(select(Country)).scalars().all()
    return [Country(id=country.id, name=country.name, code=country.code) for country in countries]


@router.post("/", response_model=Country)
async def create_country(
        country: Country, 
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    country_exist = session.query(Country).filter(Country.name == country.name).first()
    if country_exist:
        raise HTTPException(status_code=400, detail="Country already exists")
    country = Country(name=country.name, code=country.code)
    session.add(country)
    await session.commit()
    await session.refresh(country)
    return country


@router.get("/{country_id}", response_model=Country)
async def get_country(
        country_id: int, 
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    country = await session.get(Country, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.put("/{country_id}")
async def update_country(
        country_id: int, 
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    return {"country": country_id}


@router.delete("/{country_id}")
async def delete_country(
        country_id: int, 
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
    ):
    return {"country": country_id}

@router.get("/populate")
async def populate_initial_countries():
    from app.populate.countries import populate_countries
    countries = get_countries()
    if not countries:
        populate_countries()
        return {"message": "Countries populated"}
    else:
        return {"message": "Countries already populated"}

