# agent/scheduler_tools.py
"""Followup queue for agent-driven self-scheduling.

Agents call schedule_followup_internal() to enqueue a proactive message
after a delay. APScheduler's _proactive_monitor() pops from this queue
on each 5-second tick and routes it into the pending_proactive mechanism.
"""
from threading import Timer

_followup_queue: list[str] = []


def _enqueue(message: str) -> None:
    _followup_queue.append(message)


def schedule_followup_internal(message: str, delay_seconds: float) -> None:
    Timer(delay_seconds, _enqueue, args=[message]).start()


def pop_followup() -> str | None:
    return _followup_queue.pop(0) if _followup_queue else None
