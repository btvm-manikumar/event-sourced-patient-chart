from __future__ import annotations

from fastapi import FastAPI

from app.api.patient_events import router as patient_events_router
from app.api.patient_state import router as patient_state_router
from app.database.database import Base, engine

# Import models so tables are created.
from app.database import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event-Sourced Patient Chart",
    version="1.0.0",
    description="Immutable event-sourced patient chart with time-travel queries and snapshot-based reconstruction.",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "Event-Sourced Patient Chart",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": "sqlite"}


app.include_router(patient_events_router)
app.include_router(patient_state_router)
