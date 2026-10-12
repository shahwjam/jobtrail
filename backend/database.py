from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

# Connection string: dialect+driver://user:password@host/dbname — read from
# the DATABASE_URL environment variable so the same code runs on your Mac,
# inside Docker, and in the cloud (see config.py for the local default).
# pool_pre_ping checks a pooled connection is still alive before using it,
# which matters on cloud databases that drop idle connections.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency: hands an endpoint a database session, then closes it after.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
