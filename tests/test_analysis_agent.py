# tests/test_analysis_agent.py
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage


def test_build_analysis_agent_returns_graph():
    with patch("agent.analysis_agent.get_llm") as mock_get_llm, \
         patch("agent.analysis_agent.create_agent") as mock_create:
        mock_get_llm.return_value = MagicMock()
        mock_create.return_value = MagicMock()
        from agent.analysis_agent import build_analysis_agent
        graph = build_analysis_agent()
        assert graph is not None


def test_build_analysis_agent_accepts_custom_model():
    with patch("agent.analysis_agent.get_llm") as mock_get_llm, \
         patch("agent.analysis_agent.create_agent") as mock_create:
        mock_get_llm.return_value = MagicMock()
        mock_create.return_value = MagicMock()
        from agent.analysis_agent import build_analysis_agent
        build_analysis_agent(model="gpt-4o")
        mock_get_llm.assert_called_once_with("gpt-4o")


def test_invoke_analysis_agent_returns_string():
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "messages": [AIMessage(content="近7天心率平均 74 bpm，趨勢穩定。")]
    }
    from agent.analysis_agent import invoke_analysis_agent
    result = invoke_analysis_agent(mock_graph, "近7天健康趨勢")
    assert isinstance(result, str)
    assert "心率" in result
