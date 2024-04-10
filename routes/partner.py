from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Partner, PartnerBase, PartnerCreate, User, Account
from security import oauth2_scheme, get_current_active_user
from routes.account import verify_account_project_user


router = APIRouter(
    prefix="/accounts/partners",
    tags=["accounts"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{project_id}/{account_id}", response_model=list[Partner])
async def get_partners(
    project_id: int,
    account_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(Account.id == account_id)

    if not current_user.is_superuser:
        if verify_account_project_user(
            account_id, project_id, current_user.id, session
        ):
            raise HTTPException(status_code=403, detail="Not allowed")

    account = session.exec(statement).first()
    if not account or account.project.id != project_id:
        raise HTTPException(status_code=404, detail="Account not found")
    return account.partners


@router.post("/{project_id}/{account_id}", response_model=Partner)
async def create_partner(
    project_id: int,
    account_id: int,
    partner: PartnerCreate,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(Account.id == account_id)

    if not current_user.is_superuser:
        if verify_account_project_user(
            account_id, project_id, current_user.id, session
        ):
            raise HTTPException(status_code=403, detail="Not allowed")

    account = session.exec(statement).first()
    if not account or account.project.id != project_id:
        raise HTTPException(status_code=404, detail="Account not found")
    partner_exist = session.exec(statement).first()
    if partner_exist:
        raise HTTPException(status_code=400, detail="Partner already exists")
    partner = Partner(
        name=partner.name,
        description=partner.description,
        percentage=partner.percentage,
        account_id=account_id,
    )
    session.add(partner)
    session.commit()
    session.refresh(partner)
    return partner


@router.get("/{project_id}/{account_id}/{partner_id}", response_model=Partner)
async def get_partner(
    project_id: int,
    account_id: int,
    partner_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(Account.id == account_id)

    if not current_user.is_superuser:
        if verify_account_project_user(
            account_id, project_id, current_user.id, session
        ):
            raise HTTPException(status_code=403, detail="Not allowed")

    account = session.exec(statement).first()
    if not account or account.project.id != project_id:
        raise HTTPException(status_code=404, detail="Account not found")
    statement = select(Partner).filter(
        Partner.account_id == account_id,
    )
    partner = session.exec(statement).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@router.patch("/{project_id}/{account_id}/{partner_id}")
async def update_partner(
    project_id: int,
    account_id: int,
    partner_id: int,
    partner: PartnerBase,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(Account.id == account_id)

    if not current_user.is_superuser:
        if verify_account_project_user(
            account_id, project_id, current_user.id, session
        ):
            raise HTTPException(status_code=403, detail="Not allowed")

    account = session.exec(statement).first()
    if not account or account.project.id != project_id:
        raise HTTPException(status_code=404, detail="Account not found")
    statement = select(Partner).filter(
        Partner.account_id == account_id,
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


@router.delete("/{project_id}/{account_id}/{partner_id}")
async def delete_partner(
    project_id: int,
    account_id: int,
    partner_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    statement = select(Account).filter(Account.id == account_id)

    if not current_user.is_superuser:
        if verify_account_project_user(
            account_id, project_id, current_user.id, session
        ):
            raise HTTPException(status_code=403, detail="Not allowed")

    account = session.exec(statement).first()
    if not account or account.project.id != project_id:
        raise HTTPException(status_code=404, detail="Account not found")
    partner = session.exec(statement).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    session.delete(partner)
    session.commit()
    return {"ok": True}
