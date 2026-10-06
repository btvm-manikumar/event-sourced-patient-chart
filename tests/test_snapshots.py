from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.event_sourcing.snapshots import create_snapshot, get_latest_snapshot


def test_snapshot_creation_and_lookup() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        state = {"patient_id": "PAT-4001", "first_name": "Avery", "diagnoses": [{"description": "Hypothyroidism"}]}
        snapshot = create_snapshot(db, "PAT-4001", state, version=2, last_event_sequence=2)
        latest = get_latest_snapshot(db, "PAT-4001")

        assert snapshot.patient_id == "PAT-4001"
        assert latest is not None
        assert latest.state["first_name"] == "Avery"
    finally:
        db.close()
