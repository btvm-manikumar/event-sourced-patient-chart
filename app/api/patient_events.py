from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.event_sourcing.event_store import OptimisticConcurrencyError, append_event, list_events
from app.event_sourcing.events import EventModel
from app.schemas.events import EventCreateRequest

router = APIRouter(prefix="/patients", tags=["patient-events"])


@router.post("/{patient_id}/events", response_model=EventModel)
def create_patient_event(
    patient_id: str,
    payload: EventCreateRequest,
    db: Session = Depends(get_db),
):
    event = EventModel(
        patient_id=patient_id,
        event_type=payload.event_type,
        event_version=payload.event_version,
        occurred_at=payload.occurred_at or EventModel.model_fields["occurred_at"].default_factory(),
        actor_id=payload.actor_id,
        source=payload.source,
        payload=payload.payload,
        correlation_id=payload.correlation_id or EventModel.model_fields["correlation_id"].default_factory(),
        causation_id=payload.causation_id,
    )
    try:
        return append_event(db, event, expected_version=payload.expected_version)
    except OptimisticConcurrencyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{patient_id}/events", response_model=list[EventModel])
def list_patient_events(patient_id: str, db: Session = Depends(get_db)):
    return list_events(db, patient_id)


@router.get("/{patient_id}/events/latest", response_model=EventModel | None)
def latest_patient_event(patient_id: str, db: Session = Depends(get_db)):
    events = list_events(db, patient_id)
    return events[-1] if events else None
