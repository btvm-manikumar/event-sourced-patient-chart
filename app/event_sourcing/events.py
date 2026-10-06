from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventModel(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    patient_id: str
    event_type: str
    event_version: int = 1
    sequence_number: int | None = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: str = "synthetic-system"
    source: str = "synthetic-clinical-system"
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    causation_id: str | None = None
    event_hash: str | None = None

    @staticmethod
    def canonical_json(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

    def compute_hash(self) -> str:
        payload = self.model_dump(exclude={"event_hash"}, exclude_none=True)
        payload["occurred_at"] = payload["occurred_at"].isoformat() if isinstance(payload.get("occurred_at"), datetime) else payload.get("occurred_at")
        payload["recorded_at"] = payload["recorded_at"].isoformat() if isinstance(payload.get("recorded_at"), datetime) else payload.get("recorded_at")
        canonical = self.canonical_json(payload)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def model_post_init(self, __context: Any) -> None:
        if self.event_hash is None:
            self.event_hash = self.compute_hash()

    @classmethod
    def from_row(cls, row: Any) -> "EventModel":
        payload = row.payload or {}
        if isinstance(payload, str):
            payload = json.loads(payload)
        return cls(
            event_id=row.event_id,
            patient_id=row.patient_id,
            event_type=row.event_type,
            event_version=row.event_version,
            sequence_number=row.sequence_number,
            occurred_at=row.occurred_at,
            recorded_at=row.recorded_at,
            actor_id=row.actor_id,
            source=row.source,
            payload=payload,
            correlation_id=row.correlation_id,
            causation_id=row.causation_id,
            event_hash=row.event_hash,
        )

    def to_record_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "patient_id": self.patient_id,
            "event_type": self.event_type,
            "event_version": self.event_version,
            "sequence_number": self.sequence_number,
            "occurred_at": self.occurred_at,
            "recorded_at": self.recorded_at,
            "actor_id": self.actor_id,
            "source": self.source,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "event_hash": self.compute_hash(),
        }
