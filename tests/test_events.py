from app.event_sourcing.events import EventModel


def test_event_model_generates_hash() -> None:
    event = EventModel(
        patient_id="PAT-1001",
        event_type="DiagnosisAdded",
        payload={"diagnosis_code": "I10", "description": "Hypertension"},
        actor_id="doctor-101",
    )

    assert event.event_hash
    assert event.event_hash == event.compute_hash()
    assert event.sequence_number is None
