from __future__ import annotations

from typing import Any, Iterable


class AggregateRoot:
    """Base class for aggregates that reconstruct state from events."""

    def __init__(self, patient_id: str | None = None):
        self.patient_id = patient_id
        self.version = 0
        self.state: dict[str, Any] = {}

    def apply_event(self, event: Any) -> None:
        raise NotImplementedError

    def apply_events(self, events: Iterable[Any]) -> None:
        for event in events:
            self.apply_event(event)
            self.version = max(self.version, int(getattr(event, "sequence_number", 0) or 0))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.state)
