from sqlmodel import Session, select
from models import User
from database import engine
from settings import settings
from security import get_password_hash


def create_first_user():
    with Session(engine) as session:
        statement = select(User).where(
                      User.username == settings['FIRST_SUPERUSER']
                    )
        user = session.exec(statement).first()
        if not user:
            user = User(
                     username=settings['FIRST_SUPERUSER'],
                     password=get_password_hash(
                                settings['FIRST_SUPERUSER_PASSWORD']
                              ),
                     is_superuser=True
                   )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        return {"message": "First user already exists"}
