# agent/alert_agent.py
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from agent.llm_factory import get_llm
from agent.tools import get_vitals, send_emergency_alert, schedule_followup
from agent.prompts import build_alert_prompt

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"


def build_alert_agent(model: str = DEFAULT_MODEL):
    """Build the AlertAgent with the given model (default: gpt-4o-mini)."""
    llm = get_llm(model)
    return create_agent(
        llm,
        tools=[get_vitals, send_emergency_alert, schedule_followup],
        system_prompt=build_alert_prompt(),
    )


def invoke_alert_agent(graph, situation: str) -> str:
    """Invoke the alert agent with a situation description, return action summary."""
    result = graph.invoke({"messages": [HumanMessage(content=situation)]})
    last = result["messages"][-1]
    return last.content if hasattr(last, "content") else str(last)
