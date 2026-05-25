# agent/alert_agent.py
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from agent.tools import get_vitals, send_emergency_alert
from agent.prompts import build_alert_prompt

load_dotenv()


def build_alert_agent():
    """Build the AlertAgent using gpt-4o-mini (fast response for emergencies)."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return create_agent(
        llm,
        tools=[get_vitals, send_emergency_alert],
        system_prompt=build_alert_prompt(),
    )


def invoke_alert_agent(graph, situation: str) -> str:
    """Invoke the alert agent with a situation description, return action summary."""
    result = graph.invoke({"messages": [HumanMessage(content=situation)]})
    last = result["messages"][-1]
    return last.content if hasattr(last, "content") else str(last)
