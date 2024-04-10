from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Partner, PartnerBase, PartnerCreate, User
from security import oauth2_scheme, get_current_active_user


router = APIRouter(
    prefix="/partners/partners",
    tags=["accounts", "partners"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{account_id}", response_model=list[Partner])
async def get_partners(
    account_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Partner).filter(
            Partner.account_id == account_id, )
    else:
        statement = select(Partner).filter(
            Partner.account_id == account_id,
            Partner.account.project.owner_id == current_user.id,
        )
    partners = session.exec(statement).all()
    return partners


@router.post("/{account_id}", response_model=Partner)
async def create_partner(
    account_id: int,
    partner: PartnerCreate,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Partner).filter(
            Partner.name == partner.name,
            Partner.account_id == account_id,
        )
    else:
        statement = select(Partner).filter(
            Partner.name == partner.name,
            Partner.account_id == account_id,
            Partner.account.project.owner_id == current_user.id,
        )
    partner_exist = session.exec(statement).first()
    if partner_exist:
        raise HTTPException(status_code=400, detail="Partner already exists")
    partner = Partner(
        name=partner.name,
        description=partner.description,
        initial_date=partner.initial_date,
        percentage=partner.percentage,
        account_id=account_id,
    )
    session.add(partner)
    session.commit()
    session.refresh(partner)
    return partner


@router.get("/{account_id}/{partner_id}", response_model=Partner)
async def get_partner(
    account_id: int,
    partner_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Partner).filter(
            Partner.account_id == account_id,
        )
    else:
        statement = select(Partner).filter(
            Partner.account_id == account_id,
            Partner.account.project.owner_id == current_user.id,
        )
    partner = session.exec(statement).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@router.patch("/{account_id}/{partner_id}")
async def update_partner(
    account_id: int,
    partner_id: int,
    partner: PartnerBase,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Partner).filter(
            Partner.account_id == account_id,
        )
    else:
        statement = select(Partner).filter(
            Partner.account_id == account_id,
            Partner.account.project.owner_id == current_user.id,
        )
    db_partner = session.exec(statement).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    partner_data = partner.model_dump(exclude_unset=True)
    for key, value in partner_data.items():
        setattr(db_partner, key, value)
    session.add(db_partner)
    session.commit()
    session.refresh(db_partner)
    return db_partner


@router.delete("/{account_id}/{partner_id}")
async def delete_partner(
    account_id: int,
    partner_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Partner).filter(
            Partner.account_id == account_id,
        )
    else:
        statement = select(Partner).filter(
            Partner.account_id == account_id,
            Partner.account.project.owner_id == current_user.id,
        )
    partner = session.exec(statement).first()
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    session.delete(partner)
    session.commit()
    return {"ok": True}
