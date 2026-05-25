# tests/test_health_agent.py
from unittest.mock import patch, MagicMock
import agent.health_agent  # noqa: F401


def test_build_agent_returns_runnable():
    with patch("agent.health_agent.ChatAnthropic") as mock_cls:
        mock_cls.return_value = MagicMock()
        from agent.health_agent import build_agent
        assert build_agent() is not None


def test_invoke_agent_returns_string():
    with patch("agent.health_agent.ChatAnthropic") as mock_cls:
        mock_cls.return_value = MagicMock()
        with patch("agent.health_agent.wrap_with_memory") as mock_wrap:
            mock_agent = MagicMock()
            mock_agent.invoke.return_value = {"output": "阿嬤早安！"}
            mock_wrap.return_value = mock_agent
            from agent.health_agent import build_agent, invoke_agent
            result = invoke_agent(build_agent(), "你好")
            assert isinstance(result, str)
            assert result == "阿嬤早安！"
