from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventCreateRequest(BaseModel):
    event_type: str
    event_version: int = 1
    occurred_at: datetime | None = None
    actor_id: str = "synthetic-system"
    source: str = "synthetic-clinical-system"
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None
    causation_id: str | None = None
    expected_version: int | None = None


class EventStateResponse(BaseModel):
    patient_id: str
    version: int
    state: dict[str, Any]
