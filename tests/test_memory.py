"""Tests for session memory management."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage
from agent.memory import get_session_history, clear_session


def test_session_created_on_first_access():
    """Test that a new session is created on first access."""
    session = get_session_history("new-session-1")
    assert session is not None


def test_sessions_are_isolated():
    """Test that different sessions maintain separate histories."""
    h1 = get_session_history("iso-a")
    h2 = get_session_history("iso-b")

    h1.add_message(HumanMessage(content="hello"))

    assert len(h2.messages) == 0
    assert len(h1.messages) == 1


def test_session_persists_across_calls():
    """Test that session history persists across multiple calls."""
    h = get_session_history("persist-test")
    h.add_message(HumanMessage(content="remember me"))

    # Fetch the same session again
    h_again = get_session_history("persist-test")
    assert len(h_again.messages) == 1
    assert h_again.messages[0].content == "remember me"


def test_clear_session_resets_history():
    """Test that clearing a session removes all messages."""
    h = get_session_history("clear-test")
    h.add_message(HumanMessage(content="to be cleared"))

    assert len(h.messages) == 1

    clear_session("clear-test")

    h_cleared = get_session_history("clear-test")
    assert len(h_cleared.messages) == 0


def test_session_with_multiple_message_types():
    """Test session storing both human and AI messages."""
    session_id = "multi-msg-test"
    h = get_session_history(session_id)

    h.add_message(HumanMessage(content="Hi there"))
    h.add_message(AIMessage(content="Hello! How can I help?"))

    h_again = get_session_history(session_id)
    assert len(h_again.messages) == 2
    assert isinstance(h_again.messages[0], HumanMessage)
    assert isinstance(h_again.messages[1], AIMessage)
