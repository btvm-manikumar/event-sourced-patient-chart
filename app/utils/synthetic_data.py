from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.event_sourcing.events import EventModel


def synthetic_patient(patient_id: str = "PAT-1001") -> dict:
    return {
        "patient_id": patient_id,
        "first_name": "Jordan",
        "last_name": "Lee",
        "date_of_birth": "1987-03-22",
        "gender": "female",
        "allergies": [],
        "diagnoses": [],
        "medications": [],
        "encounters": [],
        "notes": [],
    }


def synthetic_event_stream(patient_id: str = "PAT-1001") -> list[EventModel]:
    now = datetime.now(timezone.utc)
    return [
        EventModel(
            patient_id=patient_id,
            event_type="PatientCreated",
            event_version=1,
            sequence_number=1,
            occurred_at=now - timedelta(days=30),
            actor_id="admin-001",
            source="synthetic-registration",
            payload={
                "first_name": "Jordan",
                "last_name": "Lee",
                "date_of_birth": "1987-03-22",
                "gender": "female",
            },
        ),
        EventModel(
            patient_id=patient_id,
            event_type="DiagnosisAdded",
            event_version=1,
            sequence_number=2,
            occurred_at=now - timedelta(days=20),
            actor_id="doctor-101",
            source="synthetic-clinical-system",
            payload={
                "diagnosis_code": "I10",
                "description": "Hypertension",
            },
        ),
        EventModel(
            patient_id=patient_id,
            event_type="MedicationAdded",
            event_version=1,
            sequence_number=3,
            occurred_at=now - timedelta(days=10),
            actor_id="doctor-101",
            source="synthetic-clinical-system",
            payload={
                "medication_name": "Lisinopril",
                "dosage": "10mg",
                "frequency": "daily",
            },
        ),
    ]
