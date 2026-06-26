from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="Applied")
    job_description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
