# tests/test_alert_agent.py
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage


def test_build_alert_agent_returns_graph():
    with patch("agent.alert_agent.ChatOpenAI") as mock_cls, \
         patch("agent.alert_agent.create_agent") as mock_create:
        mock_cls.return_value = MagicMock()
        mock_create.return_value = MagicMock()
        from agent.alert_agent import build_alert_agent
        graph = build_alert_agent()
        assert graph is not None


def test_invoke_alert_agent_returns_string():
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "messages": [AIMessage(content="已通報 陳大文（0912-345-678）：心率 125 bpm")]
    }
    from agent.alert_agent import invoke_alert_agent
    result = invoke_alert_agent(mock_graph, "心率 125 bpm，血氧 88%")
    assert isinstance(result, str)
    assert "陳大文" in result
