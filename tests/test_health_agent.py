# tests/test_health_agent.py
from unittest.mock import patch, MagicMock

def test_build_agent_returns_agent_with_memory():
    with patch("agent.health_agent.ChatAnthropic") as mock_llm_cls:
        mock_llm_cls.return_value = MagicMock()
        with patch("agent.health_agent.create_agent") as mock_create:
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
