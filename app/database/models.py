import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.database.database import Base


class EventRecord(Base):
    __tablename__ = "event_store"

    event_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    event_version = Column(Integer, nullable=False, default=1)
    sequence_number = Column(Integer, nullable=False, default=1)
    occurred_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actor_id = Column(String, nullable=False)
    source = Column(String, nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    correlation_id = Column(String, nullable=False, default=lambda: str(uuid.uuid4()))
    causation_id = Column(String, nullable=True)
    event_hash = Column(String, nullable=False)

    __table_args__ = ({"sqlite_autoincrement": True},)


class SnapshotRecord(Base):
    __tablename__ = "snapshots"

    snapshot_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, nullable=False, index=True)
    version = Column(Integer, nullable=False)
    snapshot_timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_event_sequence = Column(Integer, nullable=False)
    state = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
