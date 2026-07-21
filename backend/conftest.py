import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from database import Base, get_db
from main import app

# A separate SQLite database file, just for tests — never touches jobtrail
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    # Fresh tables before each test
    Base.metadata.create_all(bind=engine)

    # Override the real get_db so endpoints use the TEST database
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    # Wipe everything after each test — total isolation
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
