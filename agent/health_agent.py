"""LangChain agent assembly for the HomeWellness Companion."""

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

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
    """Build a LangChain tool-calling agent with memory support.

    Returns:
        RunnableWithMessageHistory: Agent wrapped with message history management.
    """
    llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    llm_with_tools = llm.bind_tools(_TOOLS)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm_with_tools | RunnablePassthrough()
    return wrap_with_memory(chain)


def invoke_agent(agent_with_memory, user_input: str, session_id: str = "default") -> str:
    """Invoke the agent with user input and return the response.

    Args:
        agent_with_memory: Agent wrapped with message history.
        user_input: User's input message.
        session_id: Session identifier for memory management (default: "default").

    Returns:
        str: Agent's response.
    """
    result = agent_with_memory.invoke(
        {
            "input": user_input,
            "system_prompt": build_system_prompt(),
        },
        config={"configurable": {"session_id": session_id}},
    )
    # Extract text from result
    if hasattr(result, "content"):
        return result.content
    if isinstance(result, dict) and "output" in result:
        return result["output"]
    if isinstance(result, str):
        return result
    return str(result)
