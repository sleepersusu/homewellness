import pytest
from agent.prompts import build_system_prompt


def test_prompt_contains_name():
    """Test that system prompt includes the user's name."""
    prompt = build_system_prompt()
    assert "陳阿嬤" in prompt


def test_prompt_contains_conditions():
    """Test that system prompt includes health conditions."""
    prompt = build_system_prompt()
    assert "高血壓" in prompt
    assert "輕度糖尿病" in prompt


def test_prompt_contains_medication_time():
    """Test that system prompt includes medication times."""
    prompt = build_system_prompt()
    assert "08:00" in prompt
    assert "13:00" in prompt
    assert "19:00" in prompt


def test_prompt_contains_behavior_rules():
    """Test that system prompt includes key behavior rules."""
    prompt = build_system_prompt()
    assert "繁體中文" in prompt
    assert "醫療診斷" in prompt
