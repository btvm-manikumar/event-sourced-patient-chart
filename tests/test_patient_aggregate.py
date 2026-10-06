from app.event_sourcing.events import EventModel
from app.event_sourcing.patient_aggregate import PatientAggregate


def test_patient_aggregate_replays_state() -> None:
    events = [
        EventModel(
            patient_id="PAT-2001",
            event_type="PatientCreated",
            sequence_number=1,
            payload={"first_name": "Dana", "last_name": "Stone", "date_of_birth": "1990-01-15", "gender": "female"},
        ),
        EventModel(
            patient_id="PAT-2001",
            event_type="DiagnosisAdded",
            sequence_number=2,
            payload={"diagnosis_code": "E11", "description": "Type 2 diabetes"},
        ),
    ]

    aggregate = PatientAggregate.from_events("PAT-2001", events)
    state = aggregate.to_dict()

    assert state["first_name"] == "Dana"
    assert state["last_name"] == "Stone"
    assert len(state["diagnoses"]) == 1
    assert state["diagnoses"][0]["description"] == "Type 2 diabetes"
