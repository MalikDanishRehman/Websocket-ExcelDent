"""Helpers for HH:MM time strings used in appointment payloads."""

from __future__ import annotations

from datetime import datetime, timedelta

# Backend accepts 15–30 minute slots; default slot length for auto end_time.
DEFAULT_SLOT_MINUTES = 30


def hhmm_plus_minutes(start_hhmm: str, minutes: int = DEFAULT_SLOT_MINUTES) -> str:
    """Return end time as HH:mm given start time and duration."""
    base = datetime.strptime(start_hhmm.strip(), "%H:%M")
    return (base + timedelta(minutes=minutes)).strftime("%H:%M")
