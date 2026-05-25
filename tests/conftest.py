# tests/conftest.py
import pytest


@pytest.fixture(autouse=True)
def reset_memory_store():
    """Reset the in-memory session store before each test to prevent cross-test contamination."""
    import agent.memory as mem

    mem._store.clear()
    yield
    mem._store.clear()
