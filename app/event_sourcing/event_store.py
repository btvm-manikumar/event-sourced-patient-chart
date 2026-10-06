from __future__ import annotations

from typing import Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import EventRecord
from app.event_sourcing.events import EventModel


class OptimisticConcurrencyError(RuntimeError):
    """Raised when the expected version does not match the stored sequence."""


def latest_sequence_number(db: Session, patient_id: str) -> int:
    row = (
        db.query(func.max(EventRecord.sequence_number))
        .filter(EventRecord.patient_id == patient_id)
        .scalar()
    )
    return int(row or 0)


def append_event(db: Session, event: EventModel, expected_version: int | None = None) -> EventModel:
    current_version = latest_sequence_number(db, event.patient_id)
    if expected_version is not None and current_version != expected_version:
        raise OptimisticConcurrencyError(
            f"Optimistic concurrency conflict for patient {event.patient_id}. "
            f"Expected version {expected_version}, found {current_version}."
        )

    next_sequence = current_version + 1
    if event.sequence_number is None:
        event.sequence_number = next_sequence
    if event.event_hash is None:
        event.event_hash = event.compute_hash()

    record = EventRecord(**event.to_record_dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return EventModel.from_row(record)


def list_events(db: Session, patient_id: str) -> list[EventModel]:
    rows = (
        db.query(EventRecord)
        .filter(EventRecord.patient_id == patient_id)
        .order_by(EventRecord.sequence_number.asc())
        .all()
    )
    return [EventModel.from_row(record) for record in rows]


def append_events(db: Session, events: Sequence[EventModel]) -> list[EventModel]:
    stored: list[EventModel] = []
    for event in events:
        stored.append(append_event(db, event))
    return stored
