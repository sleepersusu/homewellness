# Code Style — HomeWellness Companion

## General

- **Python 版本**：3.10+（使用 `X | Y` union type）
- **Formatter**：black（line length 88）+ isort，或 ruff

## Naming Conventions

- **Class**：PascalCase（`_AgentWithMemory`, `BackgroundScheduler`）
- **Functions / Methods / Variables**：snake_case（`build_agent`, `invoke_agent`, `get_vitals`）
- **Constants**：UPPER_SNAKE_CASE（`_PROFILE_PATH` 私有常數除外）
- **Modules**：snake_case（`health_agent.py`, `mock_sensors.py`）

## Type Hints（必須）

所有函式參數與回傳值都必須加型別標注。

```python
def build_agent() -> _AgentWithMemory: ...
def invoke_agent(agent_with_memory: _AgentWithMemory, user_input: str, session_id: str = "default") -> str: ...
def get_session_history(session_id: str) -> InMemoryChatMessageHistory: ...
def get_mock_vitals() -> dict[str, int | float | str]: ...
```

## LangChain Tool Docstrings

`@tool` 函式的 docstring 是 tool description，LLM 靠它決策。必須清楚、中文、說明觸發情境。

```python
@tool
def get_vitals() -> dict:
    """讀取即時生理數據：心率（heart_rate bpm）、血氧（spo2 %）、環境溫度（temperature °C）。
    當用戶提到頭暈、不舒服、胸悶、身體異常時使用此工具。"""
```

## Prompt Builder Pattern

Prompt 函式從 `health_profile.json` 動態讀取數據，不硬寫病患資料：

```python
def build_care_prompt() -> str:
    profile = _load_profile()
    name = profile["name"]
    # 用 f-string 組裝，不直接寫「陳阿嬤」在程式碼
    return f"你是{name}的健康伴侶..."
```

## Error Handling

- `@tool` 函式回傳 `{"error": "說明"}` dict，不 raise exception（避免中斷 agent）
- Mock sensor 函式：`days < 1` 才 raise `ValueError`（因為是內部 util，不是 LLM tool）

```python
# Tool（對外）— 回傳 error dict
@tool
def get_health_trend(days: int = 7) -> dict:
    if days < 1:
        return {"error": "days 必須 >= 1"}

# Mock util（內部）— 可以 raise
def get_mock_health_history(days: int) -> list[dict]:
    if days < 1:
        raise ValueError(f"days must be >= 1, got {days}")
```

## Async

此專案**不使用** async/await（Streamlit 同步模型，APScheduler 背景執行緒）。LangChain agent 呼叫都是同步的。

## 路徑處理

避免 cwd 依賴，使用 `Path(__file__)` 絕對路徑：

```python
_PROFILE_PATH = Path(__file__).parent.parent / "data" / "health_profile.json"
```

## Logging

```python
import logging
logger = logging.getLogger(__name__)
logger.info("[Agent] 呼叫 AnalysisAgent，query=%s", query)
logger.error("[緊急通報] 發送失敗，reason=%s", reason, exc_info=True)
```
