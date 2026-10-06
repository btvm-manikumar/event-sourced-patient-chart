from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.event_sourcing.event_store import append_event, list_events
from app.event_sourcing.events import EventModel


def test_append_event_and_read_back() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        event = EventModel(
            patient_id="PAT-1001",
            event_type="PatientCreated",
            payload={"first_name": "Jordan", "last_name": "Lee"},
            actor_id="admin-001",
        )

        stored = append_event(db, event)
        persisted = list_events(db, "PAT-1001")

        assert stored.sequence_number == 1
        assert len(persisted) == 1
        assert persisted[0].event_type == "PatientCreated"
    finally:
        db.close()
