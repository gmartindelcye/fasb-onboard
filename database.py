from sqlmodel import Session, SQLModel, create_engine, select


from settings import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=False) # change to False for production


def init_db(session: Session) -> None:
    """
    Only use if not working with Alembic
    """
    from sqlmodel import SQLModel
    from models import Bank, Country, Currency, User, Project, Partner, Account
    from db import engine
    SQLModel.metadata.create_all(engine)


# @contextmanager
def get_session() -> Session:
    with Session(engine) as session:
        yield session

