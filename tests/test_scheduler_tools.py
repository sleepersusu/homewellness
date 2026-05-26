# tests/test_scheduler_tools.py
import pytest
from agent.scheduler_tools import (
    _followup_queue, _enqueue, pop_followup,
    set_default_followup_minutes, get_default_followup_minutes,
)


@pytest.fixture(autouse=True)
def clear_queue():
    _followup_queue.clear()
    yield
    _followup_queue.clear()


def test_pop_followup_empty_returns_none():
    assert pop_followup() is None


def test_enqueue_and_pop_returns_message():
    _enqueue("阿嬤追蹤")
    assert pop_followup() == "阿嬤追蹤"


def test_pop_removes_item_from_queue():
    _enqueue("msg")
    pop_followup()
    assert pop_followup() is None


def test_enqueue_fifo_order():
    _enqueue("first")
    _enqueue("second")
    assert pop_followup() == "first"
    assert pop_followup() == "second"


def test_schedule_followup_tool_returns_confirmation():
    from unittest.mock import patch
    with patch("agent.scheduler_tools.schedule_followup_internal") as mock_sched:
        from agent.tools import schedule_followup
        result = schedule_followup.invoke({"reason": "心率異常", "delay_minutes": 30})
        assert "30" in result
        assert "排程" in result
        mock_sched.assert_called_once()


def test_get_default_followup_minutes_initial_value():
    assert get_default_followup_minutes() == 30


def test_set_default_followup_minutes_updates_value():
    set_default_followup_minutes(15)
    assert get_default_followup_minutes() == 15
    set_default_followup_minutes(30)  # 還原


def test_set_default_followup_minutes_enforces_minimum():
    set_default_followup_minutes(0)
    assert get_default_followup_minutes() == 1
    set_default_followup_minutes(30)  # 還原


def test_schedule_followup_tool_uses_global_default_when_zero():
    from unittest.mock import patch
    set_default_followup_minutes(15)
    with patch("agent.scheduler_tools.schedule_followup_internal") as mock_sched:
        from agent.tools import schedule_followup
        schedule_followup.invoke({"reason": "測試", "delay_minutes": 0})
        _, delay_seconds = mock_sched.call_args[0]
        assert delay_seconds == 900.0  # 15 分鐘 = 900 秒
    set_default_followup_minutes(30)  # 還原


def test_schedule_followup_tool_uses_explicit_delay_when_positive():
    from unittest.mock import patch
    with patch("agent.scheduler_tools.schedule_followup_internal") as mock_sched:
        from agent.tools import schedule_followup
        schedule_followup.invoke({"reason": "測試", "delay_minutes": 10})
        _, delay_seconds = mock_sched.call_args[0]
        assert delay_seconds == 600.0  # 10 分鐘 = 600 秒


def test_alert_agent_includes_schedule_followup_tool():
    from unittest.mock import patch, MagicMock
    with patch("agent.alert_agent.get_llm", return_value=MagicMock()), \
         patch("agent.alert_agent.create_agent", return_value=MagicMock()) as mock_create:
        from agent.alert_agent import build_alert_agent
        build_alert_agent()
        tools_passed = mock_create.call_args.kwargs["tools"]
        tool_names = [t.name for t in tools_passed]
        assert "schedule_followup" in tool_names
