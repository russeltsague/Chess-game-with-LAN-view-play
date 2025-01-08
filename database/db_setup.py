from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from database.model import Base

# Database URL
DATABASE_URL = 'sqlite:///chess_game.db'

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Create all tables in the database defined by the Base class
Base.metadata.create_all(engine)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(bind=engine)

# Use contextlib.contextmanager to define a context manager
@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
