# agent/analysis_agent.py
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from agent.tools import get_health_trend
from agent.prompts import build_analysis_prompt

load_dotenv()


def build_analysis_agent():
    """Build the AnalysisAgent using Claude (smart model for data reasoning)."""
    llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    return create_agent(llm, tools=[get_health_trend], system_prompt=build_analysis_prompt())


def invoke_analysis_agent(graph, query: str) -> str:
    """Invoke the analysis agent with a query, return text response."""
    result = graph.invoke({"messages": [HumanMessage(content=query)]})
    last = result["messages"][-1]
    return last.content if hasattr(last, "content") else str(last)
