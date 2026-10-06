from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.event_sourcing.event_store import list_events
from app.event_sourcing.replay import state_at_time
from app.event_sourcing.snapshots import (
    create_snapshot,
    get_latest_snapshot,
)

router = APIRouter(prefix="/patients", tags=["patient-state"])


@router.get("/{patient_id}/state")
def get_patient_state(
    patient_id: str,
    as_of: str | None = Query(default=None),
    version: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    events = list_events(db, patient_id)
    state = state_at_time(patient_id, events, as_of=as_of, version=version)
    stored_version = max(
        (event.sequence_number or 0) for event in events
    ) if events else 0

    return {
        "patient_id": patient_id,
        "version": stored_version,
        "state": state,
    }


@router.get("/{patient_id}/time-travel")
def patient_time_travel(
    patient_id: str,
    as_of: str | None = Query(default=None),
    version: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    events = list_events(db, patient_id)
    state = state_at_time(
        patient_id,
        events,
        as_of=as_of,
        version=version,
    )

    return {
        "patient_id": patient_id,
        "query": {
            "as_of": as_of,
            "version": version,
        },
        "state": state,
    }


@router.post("/{patient_id}/snapshot")
def create_patient_snapshot(
    patient_id: str,
    db: Session = Depends(get_db),
):
    events = list_events(db, patient_id)

    if not events:
        return {
            "patient_id": patient_id,
            "message": "No events found for patient",
        }

    current_state = state_at_time(patient_id, events)

    last_event_sequence = max(
        event.sequence_number or 0
        for event in events
    )

    snapshot = create_snapshot(
        db=db,
        patient_id=patient_id,
        state=current_state,
        version=last_event_sequence,
        last_event_sequence=last_event_sequence,
    )

    return {
        "snapshot_id": snapshot.snapshot_id,
        "patient_id": snapshot.patient_id,
        "version": snapshot.version,
        "last_event_sequence": snapshot.last_event_sequence,
        "snapshot_timestamp": snapshot.snapshot_timestamp,
        "state": snapshot.state,
    }


@router.get("/{patient_id}/snapshot")
def get_patient_snapshot(
    patient_id: str,
    db: Session = Depends(get_db),
):
    snapshot = get_latest_snapshot(db, patient_id)

    if snapshot is None:
        return {
            "patient_id": patient_id,
            "snapshot": None,
            "message": "No snapshot found for patient",
        }

    return {
        "snapshot_id": snapshot.snapshot_id,
        "patient_id": snapshot.patient_id,
        "version": snapshot.version,
        "last_event_sequence": snapshot.last_event_sequence,
        "snapshot_timestamp": snapshot.snapshot_timestamp,
        "state": snapshot.state,
    }