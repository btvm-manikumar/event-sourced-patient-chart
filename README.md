# Event-Sourced Patient Chart

A standalone FastAPI application that models patient history as an immutable event stream instead of a mutable CRUD record.

## Features

- Event-sourced patient chart with append-only storage
- Event replay to reconstruct the latest patient state
- Time-travel queries for historical patient state
- Snapshot support for performance optimization
- SQLite storage for local development
- Synthetic patient data only

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python run.py
   ```
4. Open Swagger UI at `http://localhost:8000/docs`

## API overview

- `GET /health`
- `POST /patients/{patient_id}/events`
- `GET /patients/{patient_id}/events`
- `GET /patients/{patient_id}/state`
- `GET /patients/{patient_id}/time-travel`

## Notes

The event table is the source of truth. State is reconstructed by replaying events, and snapshots are used as a performance optimization layer.
