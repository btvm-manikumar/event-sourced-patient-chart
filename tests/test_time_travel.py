from datetime import datetime, timedelta, timezone

from app.event_sourcing.events import EventModel
from app.event_sourcing.replay import state_at_time


def test_time_travel_replays_events_before_timestamp() -> None:
    now = datetime.now(timezone.utc)
    events = [
        EventModel(
            patient_id="PAT-3001",
            event_type="PatientCreated",
            sequence_number=1,
            occurred_at=now - timedelta(days=10),
            payload={"first_name": "Morgan", "last_name": "Wong", "gender": "male"},
        ),
        EventModel(
            patient_id="PAT-3001",
            event_type="DiagnosisAdded",
            sequence_number=2,
            occurred_at=now - timedelta(days=2),
            payload={"diagnosis_code": "J45", "description": "Asthma"},
        ),
    ]

    state = state_at_time("PAT-3001", events, as_of=(now - timedelta(days=5)).isoformat())
    assert state["first_name"] == "Morgan"
    assert state["diagnoses"] == []

    state = state_at_time("PAT-3001", events, as_of=(now - timedelta(days=1)).isoformat())
    assert len(state["diagnoses"]) == 1
