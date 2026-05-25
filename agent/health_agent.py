# agent/health_agent.py
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from agent.tools import (
    get_vitals,
    get_medication_schedule,
    get_sleep_report,
    get_health_trend,
    send_emergency_alert,
)
from agent.prompts import build_system_prompt
from agent.memory import wrap_with_memory

load_dotenv()

_TOOLS = [
    get_vitals,
    get_medication_schedule,
    get_sleep_report,
    get_health_trend,
    send_emergency_alert,
]

def build_agent():
    llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    graph = create_agent(llm, tools=_TOOLS, system_prompt=build_system_prompt())
    return wrap_with_memory(graph)

def invoke_agent(agent_with_memory, user_input: str, session_id: str = "default") -> str:
    result = agent_with_memory.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    return result["output"]
