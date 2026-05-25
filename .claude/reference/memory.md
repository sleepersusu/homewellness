# Session 記憶（agent/memory.py）

## 為什麼不用 RunnableWithMessageHistory

LangChain 1.x 的 `RunnableWithMessageHistory` 已 deprecated，且要求被包裝對象必須是 LangChain `Runnable`。`create_agent` 回傳的是 langgraph `CompiledStateGraph`，介面不完全相容，所以自建 `_AgentWithMemory`。

---

## 核心元件

### `_store`（模組層級）

```python
_store: dict[str, InMemoryChatMessageHistory] = {}
```

所有 session 共享同一個 dict。key 是 `session_id`，value 是 `InMemoryChatMessageHistory`。

### `get_session_history(session_id)`

```python
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
    return _store[session_id]
```

### `_AgentWithMemory.invoke(inputs, config)`

```python
def invoke(self, inputs: dict, config: dict | None = None) -> dict:
    session_id = (config.get("configurable") or {}).get("session_id", "default")
    history = get_session_history(session_id)
    user_input = inputs.get("input", "")

    # 組合：歷史 + 新訊息
    messages = list(history.messages) + [HumanMessage(content=user_input)]

    # 用 langgraph 格式呼叫
    result = self._executor.invoke({"messages": messages}, config=config)

    # 擷取最後一條 AI 訊息
    last = result["messages"][-1]
    output = last.content if hasattr(last, "content") else str(last)

    # 存入歷史
    history.add_message(HumanMessage(content=user_input))
    history.add_message(AIMessage(content=output))

    return {"output": output}
```

---

## 呼叫方式（CareAgent）

```python
# 建立
agent_with_memory = wrap_with_memory(graph)

# 呼叫（必須傳 input，session_id 走 configurable）
result = agent_with_memory.invoke(
    {"input": user_input},
    config={"configurable": {"session_id": "user-abc"}},
)
response = result["output"]
```

---

## 測試注意事項

`conftest.py` 有 autouse fixture 在每個 test 前後清空 `_store`：

```python
@pytest.fixture(autouse=True)
def reset_memory_store():
    import agent.memory as mem
    mem._store.clear()
    yield
    mem._store.clear()
```

這防止 test 之間互相污染 session 狀態。

---

## 子代理的記憶

AnalysisAgent 和 AlertAgent **不包記憶**。它們作為工具被呼叫，每次都是獨立的 stateless 呼叫，不需要跨呼叫的上下文。只有 CareAgent（主對話 agent）需要跨 turn 記憶。
