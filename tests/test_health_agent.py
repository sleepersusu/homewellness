# tests/test_health_agent.py
from unittest.mock import patch, MagicMock


def test_build_agent_returns_agent_with_memory():
    # Sub-agents are lazy-imported inside build_agent(), so patch at source modules
    with patch("agent.health_agent.ChatOpenAI") as mock_llm_cls, \
         patch("agent.health_agent.create_agent") as mock_create, \
         patch("agent.analysis_agent.build_analysis_agent", return_value=MagicMock()), \
         patch("agent.alert_agent.build_alert_agent", return_value=MagicMock()):
        mock_llm_cls.return_value = MagicMock()
        mock_create.return_value = MagicMock()
        from agent.health_agent import build_agent
        agent = build_agent()
        assert agent is not None


def test_invoke_agent_returns_string():
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"output": "阿嬤早安！"}
    from agent.health_agent import invoke_agent
    result = invoke_agent(mock_agent, "你好", session_id="test-session")
    assert isinstance(result, str)
    assert result == "阿嬤早安！"
