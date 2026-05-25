"""Session memory management for multi-turn conversations."""

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

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


def wrap_with_memory(runnable) -> RunnableWithMessageHistory:
    """Wrap a runnable with message history support.

    Args:
        runnable: The runnable to wrap.

    Returns:
        RunnableWithMessageHistory that manages chat context.
    """
    return RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
