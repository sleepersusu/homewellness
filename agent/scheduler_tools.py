# agent/scheduler_tools.py
"""Followup queue for agent-driven self-scheduling.

Agents call schedule_followup_internal() to enqueue a proactive message
after a delay. APScheduler's _proactive_monitor() pops from this queue
on each 5-second tick and routes it into the pending_proactive mechanism.
"""
from threading import Timer

_followup_queue: list[str] = []
_default_followup_minutes: int = 30


def set_default_followup_minutes(minutes: int) -> None:
    global _default_followup_minutes
    _default_followup_minutes = max(1, minutes)


def get_default_followup_minutes() -> int:
    return _default_followup_minutes


def _enqueue(message: str) -> None:
    _followup_queue.append(message)


def schedule_followup_internal(message: str, delay_seconds: float) -> None:
    Timer(delay_seconds, _enqueue, args=[message]).start()


def pop_followup() -> str | None:
    return _followup_queue.pop(0) if _followup_queue else None
