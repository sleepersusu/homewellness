# Testing Guidelines — HomeWellness Companion

## 基本規則

- **測試函式命名**：`test_` 前綴 + 英文描述，**禁止中文函式名稱**
- **TDD 流程**：先寫測試 → 確認 fail → 實作 → 確認 pass
- `asyncio_mode = auto`（pytest.ini 已設定，不需要 `@pytest.mark.asyncio`）

```python
# 正確
def test_build_agent_returns_agent_with_memory(): ...
def test_invoke_agent_returns_string(): ...
def test_get_vitals_returns_dict(): ...

# 禁止（中文函式名）
def test_建立代理(): ...
def test_調用代理(): ...
```

---

## 測試工具

| 工具 | 用途 |
|------|------|
| `pytest` | 測試框架 |
| `pytest-asyncio` | async 測試支援（auto 模式） |
| `pytest-cov` | 覆蓋率量測 |
| `unittest.mock` | patch Agent / LLM 呼叫，避免真實 API 請求 |

---

## conftest.py — 必要設定

每個測試前後自動清空 session 記憶，防止 test 互相污染：

```python
import pytest

@pytest.fixture(autouse=True)
def reset_memory_store():
    import agent.memory as mem
    mem._store.clear()
    yield
    mem._store.clear()
```

---

## Mock 策略

### Agent / LLM 測試：在來源模組 patch

`build_agent()` 的子代理是 lazy import，必須在**來源模組**（source module）patch，不是在 `health_agent` 命名空間：

```python
from unittest.mock import patch, MagicMock

def test_build_agent_returns_agent_with_memory():
    with patch("agent.health_agent.ChatOpenAI") as mock_llm_cls, \
         patch("agent.health_agent.create_agent") as mock_create, \
         patch("agent.analysis_agent.build_analysis_agent", return_value=MagicMock()), \
         patch("agent.alert_agent.build_alert_agent", return_value=MagicMock()):
        mock_llm_cls.return_value = MagicMock()
        mock_create.return_value = MagicMock()
        from agent.health_agent import build_agent
        agent = build_agent()
        assert agent is not None
```

### 子代理（AnalysisAgent / AlertAgent）回傳格式

必須回傳 `{"messages": [AIMessage(content="...")]}` 格式（langgraph 格式）：

```python
from langchain_core.messages import AIMessage

def test_invoke_analysis_agent_returns_string():
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "messages": [AIMessage(content="近7天心率平均 74 bpm，趨勢穩定。")]
    }
    from agent.analysis_agent import invoke_analysis_agent
    result = invoke_analysis_agent(mock_graph, "近7天健康趨勢")
    assert isinstance(result, str)
    assert "心率" in result
```

### CareAgent（_AgentWithMemory）回傳格式

CareAgent 回傳 `{"output": "..."}` 格式：

```python
def test_invoke_agent_returns_string():
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"output": "阿嬤早安！"}
    from agent.health_agent import invoke_agent
    result = invoke_agent(mock_agent, "你好", session_id="test-session")
    assert isinstance(result, str)
    assert result == "阿嬤早安！"
```

---

## 測試結構

```
tests/
├── conftest.py               # autouse fixture：清空 _store
├── test_health_agent.py      # CareAgent build + invoke
├── test_analysis_agent.py    # AnalysisAgent build + invoke
├── test_alert_agent.py       # AlertAgent build + invoke
├── test_prompts.py           # 三個 prompt 函式驗證關鍵字
├── test_tools.py             # 五個 @tool 函式
└── test_mock_sensors.py      # IoT mock 資料層
```

---

## 常用指令

```bash
pytest tests/ -v
pytest tests/ --cov=agent --cov=data --cov-report=term-missing
pytest tests/test_health_agent.py::test_build_agent_returns_agent_with_memory -v
```
