from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from app.event_sourcing.patient_aggregate import PatientAggregate


def replay_events(patient_id: str, events: Iterable[Any]) -> dict[str, Any]:
    ordered_events = sorted(events, key=lambda event: int(getattr(event, "sequence_number", 0) or 0))
    aggregate = PatientAggregate(patient_id=patient_id)
    aggregate.apply_events(ordered_events)
    return aggregate.to_dict()


def state_at_time(patient_id: str, events: Iterable[Any], as_of: str | datetime | None = None, version: int | None = None) -> dict[str, Any]:
    ordered = sorted(events, key=lambda event: int(getattr(event, "sequence_number", 0) or 0))

    if version is not None:
        ordered = [event for event in ordered if (getattr(event, "sequence_number", 0) or 0) <= version]

    if as_of is not None:
        if isinstance(as_of, str):
            as_of = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        ordered = [event for event in ordered if getattr(event, "occurred_at", None) and event.occurred_at <= as_of]

    return replay_events(patient_id, ordered)
