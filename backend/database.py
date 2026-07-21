from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string: dialect+driver://user@host/dbname
# On a default Mac Homebrew install, your Mac username is the DB user, no password.
DATABASE_URL = "postgresql+psycopg2://localhost/jobtrail"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency: hands an endpoint a database session, then closes it after.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
