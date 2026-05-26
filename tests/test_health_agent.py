# tests/test_health_agent.py
from unittest.mock import patch, MagicMock


def test_build_agent_returns_agent_with_memory():
    with patch("agent.health_agent.get_llm") as mock_get_llm, \
         patch("agent.health_agent.create_agent") as mock_create, \
         patch("agent.analysis_agent.build_analysis_agent", return_value=MagicMock()), \
         patch("agent.alert_agent.build_alert_agent", return_value=MagicMock()):
        mock_get_llm.return_value = MagicMock()
        mock_create.return_value = MagicMock()
        from agent.health_agent import build_agent
        agent = build_agent()
        assert agent is not None


def test_build_agent_passes_models_to_sub_agents():
    with patch("agent.health_agent.get_llm") as mock_get_llm, \
         patch("agent.health_agent.create_agent") as mock_create, \
         patch("agent.analysis_agent.build_analysis_agent", return_value=MagicMock()) as mock_analysis, \
         patch("agent.alert_agent.build_alert_agent", return_value=MagicMock()) as mock_alert:
        mock_get_llm.return_value = MagicMock()
        mock_create.return_value = MagicMock()
        from agent.health_agent import build_agent
        build_agent(care_model="gpt-4o", analysis_model="gemini-2.5-flash", alert_model="gpt-4o-mini")
        mock_analysis.assert_called_once_with(model="gemini-2.5-flash")
        mock_alert.assert_called_once_with(model="gpt-4o-mini")
        mock_get_llm.assert_called_once_with("gpt-4o")


def test_invoke_agent_returns_string():
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "output": "阿嬤早安！",
        "usage_metadata": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
    }
    from agent.health_agent import invoke_agent
    text, stats = invoke_agent(mock_agent, "你好", session_id="test-session")
    assert isinstance(text, str)
    assert text == "阿嬤早安！"


def test_invoke_agent_returns_stats_dict():
    """Test invoke_agent returns stats with required fields."""
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "output": "OK",
        "usage_metadata": {"input_tokens": 80, "output_tokens": 30, "total_tokens": 110},
    }
    from agent.health_agent import invoke_agent
    _, stats = invoke_agent(mock_agent, "test", session_id="test-session")
    assert "latency" in stats
    assert "input_tokens" in stats
    assert "output_tokens" in stats
    assert "total_tokens" in stats
    assert "cost_usd" in stats
    assert "model" in stats


def test_invoke_agent_latency_is_non_negative():
    """Test that latency in stats is a non-negative float."""
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "output": "OK",
        "usage_metadata": {"input_tokens": 50, "output_tokens": 20, "total_tokens": 70},
    }
    from agent.health_agent import invoke_agent
    _, stats = invoke_agent(mock_agent, "test", session_id="test")
    assert stats["latency"] >= 0.0


def test_invoke_agent_cost_is_non_negative():
    """Test that cost_usd is non-negative for known and unknown models."""
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "output": "OK",
        "usage_metadata": {"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
    }
    from agent.health_agent import invoke_agent
    _, stats = invoke_agent(mock_agent, "test", model="gpt-4o-mini")
    assert stats["cost_usd"] >= 0.0
    assert stats["cost_usd"] > 0  # gpt-4o-mini has known price
