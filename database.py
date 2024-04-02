from sqlmodel import SQLModel, Session, create_engine

from settings import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True) # change to False for production


def init_db(session: Session) -> None:
    """
    Only use if not working with Alembic
    """
    from sqlmodel import SQLModel
    from models import Bank, Country, Currency, User, Project, Partner, Account
    from db import engine
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session as session:
        yield session


