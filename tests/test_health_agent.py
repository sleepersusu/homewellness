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
    mock_agent.invoke.return_value = {"output": "阿嬤早安！"}
    from agent.health_agent import invoke_agent
    result = invoke_agent(mock_agent, "你好", session_id="test-session")
    assert isinstance(result, str)
    assert result == "阿嬤早安！"
