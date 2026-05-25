# agent/health_agent.py
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent as _create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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

# Compatibility shims — allow tests to mock these names at agent.health_agent.*
# create_agent (langchain v1) is the v1 equivalent of create_tool_calling_agent + AgentExecutor.
# We expose the v1 function under the classic names so import-level mocking works.
def create_tool_calling_agent(llm, tools, prompt):
    """Shim: build a tool-calling agent using langchain v1 create_agent."""
    return _create_agent(llm, tools)


class AgentExecutor:
    """Shim: wraps a compiled langgraph agent with an AgentExecutor-compatible interface."""

    def __init__(self, agent, tools, verbose=False):
        self._agent = agent
        self.verbose = verbose

    def invoke(self, inputs, config=None):
        messages = self._agent.invoke(inputs, config=config or {})
        # langgraph returns {"messages": [...]}; last message is the AI response
        last = messages["messages"][-1]
        content = last.content if hasattr(last, "content") else str(last)
        return {"output": content}


def build_agent():
    llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, _TOOLS, prompt)
    executor = AgentExecutor(agent=agent, tools=_TOOLS, verbose=True)
    return wrap_with_memory(executor)


def invoke_agent(agent_with_memory, user_input: str, session_id: str = "default") -> str:
    result = agent_with_memory.invoke(
        {
            "input": user_input,
            "system_prompt": build_system_prompt(),
        },
        config={"configurable": {"session_id": session_id}},
    )
    return result["output"]
