"""Session memory management for multi-turn conversations."""

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

_store: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Get or create a session's chat history.

    Args:
        session_id: Unique identifier for the session.

    Returns:
        InMemoryChatMessageHistory for the session.
    """
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
    return _store[session_id]


def clear_session(session_id: str) -> None:
    """Clear all messages from a session.

    Args:
        session_id: Unique identifier for the session to clear.
    """
    _store.pop(session_id, None)


class _AgentWithMemory:
    """Wraps any executor-like object with in-memory session history.

    Accepts any object that has an ``invoke(inputs, config=None)`` method.
    This avoids the deprecated ``RunnableWithMessageHistory`` requirement
    that the wrapped object must be a LangChain ``Runnable``.
    """

    def __init__(self, executor) -> None:
        self._executor = executor

    def invoke(self, inputs: dict, config: dict | None = None) -> dict:
        config = config or {}
        session_id = (config.get("configurable") or {}).get("session_id", "default")
        history = get_session_history(session_id)

        user_input = inputs.get("input", "")

        # Build messages list: history + new human message
        messages = list(history.messages) + [HumanMessage(content=user_input)]

        # Invoke the langgraph agent with messages format
        result = self._executor.invoke({"messages": messages}, config=config)

        # Extract output from last AI message
        last = result["messages"][-1]
        output = last.content if hasattr(last, "content") else str(last)

        # Sum token usage across all AI messages in this turn
        input_tokens = 0
        output_tokens = 0
        for msg in result["messages"]:
            meta = getattr(msg, "usage_metadata", None)
            if meta:
                input_tokens += meta.get("input_tokens", 0)
                output_tokens += meta.get("output_tokens", 0)

        # Persist exchange to history
        history.add_message(HumanMessage(content=user_input))
        history.add_message(AIMessage(content=output))

        return {
            "output": output,
            "usage_metadata": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
        }


def wrap_with_memory(runnable) -> _AgentWithMemory:
    """Wrap an executor with message history support.

    Args:
        runnable: Any object with an ``invoke`` method.

    Returns:
        _AgentWithMemory that manages chat context per session.
    """
    return _AgentWithMemory(runnable)
