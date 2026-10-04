from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
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

    # The most recent resume match score, if one has been run (one-to-one).
    match = relationship("MatchScore", uselist=False, back_populates="application", cascade="all, delete-orphan")

    @property
    def match_score(self):
        # Lets ApplicationResponse expose just the number on every card.
        return self.match.score if self.match else None


# Stored in its own table rather than as new columns on applications:
# create_all() creates missing tables on startup, but it never alters an
# existing table, so this needs no migration on databases that already exist.
class MatchScore(Base):
    __tablename__ = "match_scores"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer, ForeignKey("applications.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    score = Column(Integer, nullable=False)
    matched_keywords = Column(JSON, nullable=False, default=list)
    missing_keywords = Column(JSON, nullable=False, default=list)
    summary = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    application = relationship("Application", back_populates="match")


# Cache of Claude replies, keyed by a hash of the full request (see ai_cache.py).
# Also doubles as a log of paid API calls for the daily usage cap.
class AIResponse(Base):
    __tablename__ = "ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(64), unique=True, nullable=False, index=True)  # sha256 hex
    template_name = Column(String(100), nullable=False)
    template_version = Column(Integer, nullable=False)
    model = Column(String(100), nullable=False)
    response = Column(Text, nullable=False)
    # Set in Python (UTC) rather than by the DB, so the TTL and daily-cap
    # comparisons behave the same on Postgres and on SQLite in tests.
    created_at = Column(
        DateTime(timezone=True), nullable=False, index=True, default=lambda: datetime.now(timezone.utc)
    )
