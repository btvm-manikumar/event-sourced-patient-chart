from __future__ import annotations

from typing import Any, Iterable

from app.event_sourcing.aggregate import AggregateRoot


class PatientAggregate(AggregateRoot):
    """Rebuilds patient state by replaying patient events."""

    def __init__(self, patient_id: str | None = None):
        super().__init__(patient_id=patient_id)
        self.state = {
            "patient_id": patient_id,
            "first_name": None,
            "last_name": None,
            "date_of_birth": None,
            "gender": None,
            "allergies": [],
            "diagnoses": [],
            "medications": [],
            "encounters": [],
            "notes": [],
        }

    @classmethod
    def from_events(cls, patient_id: str, events: Iterable[Any]) -> "PatientAggregate":
        aggregate = cls(patient_id=patient_id)
        aggregate.apply_events(events)
        return aggregate

    def apply_event(self, event: Any) -> None:
        payload = getattr(event, "payload", {}) or {}
        event_type = getattr(event, "event_type", "")
        self.state["patient_id"] = getattr(event, "patient_id", self.patient_id)

        if event_type == "PatientCreated":
            self.state.update(
                {
                    "patient_id": event.patient_id,
                    "first_name": payload.get("first_name"),
                    "last_name": payload.get("last_name"),
                    "date_of_birth": payload.get("date_of_birth"),
                    "gender": payload.get("gender"),
                }
            )
        elif event_type == "DemographicsUpdated":
            self.state.update({
                key: value for key, value in payload.items() if value is not None
            })
        elif event_type == "DiagnosisAdded":
            diagnosis = payload.copy()
            if diagnosis not in self.state["diagnoses"]:
                self.state["diagnoses"].append(diagnosis)
        elif event_type in {"MedicationAdded", "MedicationPrescribed"}:
            medication = payload.copy()
            if medication not in self.state["medications"]:
                self.state["medications"].append(medication)
        elif event_type == "AllergyAdded":
            allergy = payload.copy()
            if allergy not in self.state["allergies"]:
                self.state["allergies"].append(allergy)
        elif event_type == "EncounterRecorded":
            encounter = payload.copy()
            if encounter not in self.state["encounters"]:
                self.state["encounters"].append(encounter)
        elif event_type == "ClinicalNoteAdded":
            note = payload.copy()
            if note not in self.state["notes"]:
                self.state["notes"].append(note)
        elif event_type == "PatientArchived":
            self.state["archived"] = True
            self.state["archived_reason"] = payload.get("reason")
