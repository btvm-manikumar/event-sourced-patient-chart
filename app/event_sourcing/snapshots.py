from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import SnapshotRecord


def create_snapshot(db: Session, patient_id: str, state: dict[str, Any], version: int, last_event_sequence: int) -> SnapshotRecord:
    snapshot = SnapshotRecord(
        snapshot_id=str(uuid4()),
        patient_id=patient_id,
        version=version,
        snapshot_timestamp=datetime.now(timezone.utc),
        last_event_sequence=last_event_sequence,
        state=state,
        created_at=datetime.now(timezone.utc),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_latest_snapshot(db: Session, patient_id: str) -> SnapshotRecord | None:
    return (
        db.query(SnapshotRecord)
        .filter(SnapshotRecord.patient_id == patient_id)
        .order_by(SnapshotRecord.last_event_sequence.desc())
        .first()
    )


def get_snapshot_state(db: Session, patient_id: str) -> dict[str, Any] | None:
    snapshot = get_latest_snapshot(db, patient_id)
    if snapshot is None:
        return None
    return snapshot.state
