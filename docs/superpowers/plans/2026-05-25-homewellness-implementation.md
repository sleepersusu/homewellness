# HomeWellness Companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立可運行的 Streamlit 健康 AI Agent 原型，展示主動式健康關懷、Tool Calling、兩層記憶、APScheduler 心跳機制，作為面試取回作業交付。

**Architecture:** LangChain `create_tool_calling_agent` + `RunnableWithMessageHistory` 連接 Claude claude-sonnet-4-6 與五個 IoT mock 工具。APScheduler 在背景執行緒定時輪詢感測數據，寫入 Streamlit session state 觸發主動回應。Streamlit 呈現左右分欄（數據面板 + 對話視窗）。

**Tech Stack:** Python 3.11+, langchain>=0.3.0, langchain-anthropic>=0.3.0, anthropic>=0.40.0, streamlit>=1.40.0, apscheduler>=3.10.0, python-dotenv>=1.0.0, pytest>=8.0.0

---

## File Map

| 檔案 | 職責 |
|------|------|
| `app.py` | Streamlit 入口：佈局、session state、APScheduler 初始化、對話 I/O |
| `agent/health_agent.py` | 組裝 LangChain agent：LLM + tools + prompt + memory wrapper |
| `agent/tools.py` | 五個 `@tool` 定義，包裝 mock sensor 函式 |
| `agent/prompts.py` | 從 health_profile.json 動態建立 system prompt |
| `agent/memory.py` | `InMemoryChatMessageHistory` store + `RunnableWithMessageHistory` wrapper |
| `data/mock_sensors.py` | 模擬 IoT 數據；提供 `set_simulate_abnormal()` 切換模式 |
| `data/health_profile.json` | 靜態用戶檔案：姓名、病史、用藥計畫、警報閾值 |
| `data/health_history.json` | 近 30 天生理數據記錄（腳本生成） |
| `tests/test_mock_sensors.py` | 數據結構、正常/異常模式測試 |
| `tests/test_tools.py` | Tool 回傳 schema 測試 |
| `tests/test_prompts.py` | System prompt 內容測試 |
| `tests/test_memory.py` | Session 隔離與持久化測試 |
| `tests/test_health_agent.py` | Agent 建立與呼叫 smoke test |
| `.env.example` | ANTHROPIC_API_KEY 環境變數範本 |
| `requirements.txt` | 固定版本依賴 |
| `README.md` | 一鍵啟動說明 + Demo 腳本 |

---

## Task 1: 專案骨架

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `pytest.ini`
- Create: `agent/__init__.py`
- Create: `data/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: 建立目錄結構**

```bash
mkdir -p agent data langflow docs/superpowers/plans tests
touch agent/__init__.py data/__init__.py tests/__init__.py
```

- [ ] **Step 2: 寫 requirements.txt**

```txt
langchain>=0.3.0
langchain-anthropic>=0.3.0
langchain-community>=0.3.0
anthropic>=0.40.0
streamlit>=1.40.0
apscheduler>=3.10.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

- [ ] **Step 3: 寫 .env.example**

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

- [ ] **Step 4: 寫 pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

- [ ] **Step 5: 安裝依賴**

```bash
pip install -r requirements.txt
```

預期：所有套件安裝成功，無版本衝突。

- [ ] **Step 6: 複製 .env 並填入 API Key**

```bash
cp .env.example .env
# 編輯 .env，填入真實的 ANTHROPIC_API_KEY=sk-ant-...
```

- [ ] **Step 7: Commit**

```bash
git init
git add requirements.txt .env.example pytest.ini agent/__init__.py data/__init__.py tests/__init__.py
git commit -m "chore: 初始化專案骨架"
```

---

## Task 2: Mock 數據層

**Files:**
- Create: `data/mock_sensors.py`
- Create: `data/health_profile.json`
- Create: `data/health_history.json`
- Test: `tests/test_mock_sensors.py`

- [ ] **Step 1: 寫 tests/test_mock_sensors.py（先寫測試）**

```python
# tests/test_mock_sensors.py
from data.mock_sensors import (
    get_mock_vitals,
    get_mock_sleep_report,
    get_mock_health_history,
    set_simulate_abnormal,
)

def test_get_mock_vitals_schema():
    vitals = get_mock_vitals()
    assert "heart_rate" in vitals
    assert "spo2" in vitals
    assert "temperature" in vitals
    assert "timestamp" in vitals

def test_get_mock_vitals_normal_ranges():
    set_simulate_abnormal(False)
    for _ in range(20):
        v = get_mock_vitals()
        assert 50 <= v["heart_rate"] <= 120
        assert 90 <= v["spo2"] <= 100

def test_get_mock_vitals_abnormal_mode():
    set_simulate_abnormal(True)
    v = get_mock_vitals()
    assert v["heart_rate"] > 120 or v["spo2"] < 90
    set_simulate_abnormal(False)  # cleanup

def test_get_mock_sleep_report_schema():
    report = get_mock_sleep_report()
    assert "total_hours" in report
    assert "deep_sleep_hours" in report
    assert "wake_count" in report
    assert "date" in report

def test_get_mock_health_history_length():
    assert len(get_mock_health_history(7)) == 7

def test_get_mock_health_history_schema():
    for record in get_mock_health_history(3):
        assert "date" in record
        assert "heart_rate_avg" in record
        assert "spo2_avg" in record
        assert "sleep_hours" in record
```

- [ ] **Step 2: 執行測試確認失敗**

```bash
pytest tests/test_mock_sensors.py -v
```

預期：`ImportError: No module named 'data.mock_sensors'`

- [ ] **Step 3: 寫 data/mock_sensors.py**

```python
# data/mock_sensors.py
import random
from datetime import datetime, timedelta

_simulate_abnormal: bool = False

def set_simulate_abnormal(value: bool) -> None:
    global _simulate_abnormal
    _simulate_abnormal = value

def get_mock_vitals() -> dict:
    if _simulate_abnormal:
        return {
            "heart_rate": 125,
            "spo2": 88,
            "temperature": 26.5,
            "timestamp": datetime.now().isoformat(),
        }
    return {
        "heart_rate": random.randint(65, 85),
        "spo2": random.randint(95, 99),
        "temperature": round(random.uniform(25.0, 27.0), 1),
        "timestamp": datetime.now().isoformat(),
    }

def get_mock_sleep_report() -> dict:
    return {
        "total_hours": round(random.uniform(5.5, 8.0), 1),
        "deep_sleep_hours": round(random.uniform(1.5, 2.5), 1),
        "wake_count": random.randint(0, 3),
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
    }

def get_mock_health_history(days: int = 7) -> list[dict]:
    return [
        {
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "heart_rate_avg": random.randint(68, 82),
            "spo2_avg": random.randint(95, 99),
            "sleep_hours": round(random.uniform(5.5, 8.0), 1),
        }
        for i in range(days)
    ]
```

- [ ] **Step 4: 建立 data/health_profile.json**

```json
{
  "name": "陳阿嬤",
  "age": 72,
  "conditions": ["高血壓", "輕度糖尿病"],
  "medications": [
    {"name": "降血壓藥（Amlodipine 5mg）", "time": "08:00", "with_meal": true},
    {"name": "維生素D", "time": "13:00", "with_meal": true},
    {"name": "Metformin 500mg", "time": "19:00", "with_meal": true}
  ],
  "emergency_contacts": [
    {"name": "陳大文（兒子）", "phone": "0912-345-678"}
  ],
  "alert_thresholds": {
    "heart_rate_high": 120,
    "heart_rate_low": 50,
    "spo2_low": 90
  }
}
```

- [ ] **Step 5: 生成 data/health_history.json**

```bash
python -c "
import json, random
from datetime import datetime, timedelta
history = [
    {
        'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
        'heart_rate_avg': random.randint(68, 82),
        'spo2_avg': random.randint(95, 99),
        'sleep_hours': round(random.uniform(5.5, 8.0), 1),
    }
    for i in range(30)
]
open('data/health_history.json', 'w', encoding='utf-8').write(
    json.dumps(history, ensure_ascii=False, indent=2)
)
print('health_history.json 生成完成，共', len(history), '筆')
"
```

預期：`health_history.json 生成完成，共 30 筆`

- [ ] **Step 6: 執行測試確認通過**

```bash
pytest tests/test_mock_sensors.py -v
```

預期：6 tests PASSED

- [ ] **Step 7: Commit**

```bash
git add data/ tests/test_mock_sensors.py
git commit -m "feat(data): 新增 mock IoT 感測數據層與健康檔案"
```

---

## Task 3: Tools 實作

**Files:**
- Create: `agent/tools.py`
- Test: `tests/test_tools.py`

- [ ] **Step 1: 寫 tests/test_tools.py（先寫測試）**

```python
# tests/test_tools.py
from data.mock_sensors import set_simulate_abnormal

def test_get_vitals_schema():
    from agent.tools import get_vitals
    result = get_vitals.invoke({})
    assert "heart_rate" in result
    assert "spo2" in result
    assert "temperature" in result

def test_get_medication_schedule_schema():
    from agent.tools import get_medication_schedule
    result = get_medication_schedule.invoke({})
    assert "medications" in result
    assert "name" in result
    assert len(result["medications"]) > 0

def test_get_sleep_report_schema():
    from agent.tools import get_sleep_report
    result = get_sleep_report.invoke({})
    assert "total_hours" in result
    assert "deep_sleep_hours" in result
    assert "wake_count" in result

def test_get_health_trend_schema():
    from agent.tools import get_health_trend
    result = get_health_trend.invoke({"days": 7})
    assert "avg_heart_rate" in result
    assert "avg_spo2" in result
    assert "avg_sleep_hours" in result
    assert len(result["daily_records"]) == 7

def test_send_emergency_alert_returns_confirmation():
    from agent.tools import send_emergency_alert
    result = send_emergency_alert.invoke({"reason": "心率 125 bpm"})
    assert "已通報" in result
    assert "陳大文" in result

def test_get_vitals_abnormal_mode():
    set_simulate_abnormal(True)
    from agent.tools import get_vitals
    result = get_vitals.invoke({})
    assert result["heart_rate"] > 120 or result["spo2"] < 90
    set_simulate_abnormal(False)
```

- [ ] **Step 2: 執行測試確認失敗**

```bash
pytest tests/test_tools.py -v
```

預期：`ImportError: cannot import name 'get_vitals' from 'agent.tools'`

- [ ] **Step 3: 寫 agent/tools.py**

```python
# agent/tools.py
import json
from pathlib import Path
from langchain_core.tools import tool
from data.mock_sensors import (
    get_mock_vitals,
    get_mock_sleep_report,
    get_mock_health_history,
)

_PROFILE_PATH = Path("data/health_profile.json")

def _load_profile() -> dict:
    return json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))

@tool
def get_vitals() -> dict:
    """讀取即時生理數據：心率（heart_rate bpm）、血氧（spo2 %）、環境溫度（temperature °C）。
    當用戶提到頭暈、不舒服、胸悶、身體異常時使用此工具。"""
    return get_mock_vitals()

@tool
def get_medication_schedule() -> dict:
    """查詢今日用藥計畫，回傳藥名、服用時間、是否隨餐。
    用於用藥提醒或用戶詢問今天該吃什麼藥時使用。"""
    profile = _load_profile()
    return {"name": profile["name"], "medications": profile["medications"]}

@tool
def get_sleep_report() -> dict:
    """取得昨晚睡眠報告：總時數（total_hours）、深眠時數（deep_sleep_hours）、起夜次數（wake_count）。
    用於早晨問候時主動分享，或用戶詢問睡眠狀況時。"""
    return get_mock_sleep_report()

@tool
def get_health_trend(days: int = 7) -> dict:
    """分析近 N 天生理數據趨勢（心率、血氧、睡眠平均值）。
    用於用戶詢問近期健康狀況，或提供週期性健康建議時。"""
    history = get_mock_health_history(days)
    return {
        "days": days,
        "avg_heart_rate": round(sum(r["heart_rate_avg"] for r in history) / len(history), 1),
        "avg_spo2": round(sum(r["spo2_avg"] for r in history) / len(history), 1),
        "avg_sleep_hours": round(sum(r["sleep_hours"] for r in history) / len(history), 1),
        "daily_records": history,
    }

@tool
def send_emergency_alert(reason: str) -> str:
    """當生理數據出現危險異常時，通報緊急聯絡人及診所。
    觸發條件：心率 < 50 或 > 120 bpm，或血氧 < 90%。"""
    profile = _load_profile()
    contact = profile["emergency_contacts"][0]
    confirmation = f"已通報 {contact['name']}（{contact['phone']}）：{reason}"
    print(f"[緊急通報] {confirmation}")
    return confirmation
```

- [ ] **Step 4: 執行測試確認通過**

```bash
pytest tests/test_tools.py -v
```

預期：6 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add agent/tools.py tests/test_tools.py
git commit -m "feat(agent): 實作五個 LangChain @tool 工具"
```

---

## Task 4: System Prompt

**Files:**
- Create: `agent/prompts.py`
- Test: `tests/test_prompts.py`

- [ ] **Step 1: 寫 tests/test_prompts.py**

```python
# tests/test_prompts.py
from agent.prompts import build_system_prompt

def test_prompt_contains_name():
    assert "陳阿嬤" in build_system_prompt()

def test_prompt_contains_conditions():
    assert "高血壓" in build_system_prompt()

def test_prompt_contains_medication_time():
    assert "08:00" in build_system_prompt()

def test_prompt_contains_behavior_rules():
    prompt = build_system_prompt()
    assert "繁體中文" in prompt
    assert "醫療診斷" in prompt
```

- [ ] **Step 2: 執行測試確認失敗**

```bash
pytest tests/test_prompts.py -v
```

預期：`ImportError: cannot import name 'build_system_prompt'`

- [ ] **Step 3: 寫 agent/prompts.py**

```python
# agent/prompts.py
import json
from pathlib import Path

_PROFILE_PATH = Path("data/health_profile.json")

def build_system_prompt() -> str:
    profile = json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))
    name = profile["name"]
    age = profile["age"]
    conditions = "、".join(profile["conditions"])
    meds = "\n".join(
        f"  - {m['name']}（{m['time']}，{'隨餐' if m['with_meal'] else '空腹'}）"
        for m in profile["medications"]
    )
    return f"""你是{name}的健康伴侶，像一個真心關心她的晚輩。

用戶資料：
- 姓名：{name}，{age} 歲
- 慢性病史：{conditions}
- 今日用藥計畫：
{meds}

對話規則：
- 用名字稱呼她（「{name}」或「阿嬤」），絕對不說「用戶」
- 每則訊息只說一件事，句子不超過 2 行
- 用鼓勵語氣，不製造焦慮（說「喝點水看看」，不說「你可能脫水了」）
- 繁體中文，不使用醫療術語
- 記住對話中她說過的事，讓回應有連貫感
- 遇到異常數值：先安撫 → 說明情況 → 詢問是否需要幫忙
- 不作醫療診斷，只提供生活建議"""
```

- [ ] **Step 4: 執行測試確認通過**

```bash
pytest tests/test_prompts.py -v
```

預期：4 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add agent/prompts.py tests/test_prompts.py
git commit -m "feat(agent): 新增動態 system prompt 語氣設計"
```

---

## Task 5: Memory 管理

**Files:**
- Create: `agent/memory.py`
- Test: `tests/test_memory.py`

- [ ] **Step 1: 寫 tests/test_memory.py**

```python
# tests/test_memory.py
from langchain_core.messages import HumanMessage
from agent.memory import get_session_history, clear_session

def test_session_created_on_first_access():
    assert get_session_history("new-session") is not None

def test_sessions_are_isolated():
    h1 = get_session_history("iso-a")
    h2 = get_session_history("iso-b")
    h1.add_message(HumanMessage(content="hello"))
    assert len(h2.messages) == 0

def test_session_persists_across_calls():
    h = get_session_history("persist-test")
    h.add_message(HumanMessage(content="remember me"))
    assert get_session_history("persist-test").messages[0].content == "remember me"

def test_clear_session_resets_history():
    h = get_session_history("clear-test")
    h.add_message(HumanMessage(content="to be cleared"))
    clear_session("clear-test")
    assert len(get_session_history("clear-test").messages) == 0
```

- [ ] **Step 2: 執行測試確認失敗**

```bash
pytest tests/test_memory.py -v
```

預期：`ImportError: cannot import name 'get_session_history'`

- [ ] **Step 3: 寫 agent/memory.py**

```python
# agent/memory.py
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

_store: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
    return _store[session_id]

def clear_session(session_id: str) -> None:
    _store.pop(session_id, None)

def wrap_with_memory(runnable) -> RunnableWithMessageHistory:
    return RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
```

- [ ] **Step 4: 執行測試確認通過**

```bash
pytest tests/test_memory.py -v
```

預期：4 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add agent/memory.py tests/test_memory.py
git commit -m "feat(agent): 實作 RunnableWithMessageHistory 兩層記憶管理"
```

---

## Task 6: Agent 組裝

**Files:**
- Create: `agent/health_agent.py`
- Test: `tests/test_health_agent.py`

- [ ] **Step 1: 寫 tests/test_health_agent.py**

```python
# tests/test_health_agent.py
from unittest.mock import patch, MagicMock

def test_build_agent_returns_runnable():
    with patch("agent.health_agent.ChatAnthropic") as mock_cls:
        mock_cls.return_value = MagicMock()
        from agent.health_agent import build_agent
        assert build_agent() is not None

def test_invoke_agent_returns_string():
    with patch("agent.health_agent.ChatAnthropic") as mock_cls:
        mock_cls.return_value = MagicMock()
        with patch("agent.health_agent.AgentExecutor") as mock_exec_cls:
            mock_exec_cls.return_value = MagicMock()
            with patch("agent.health_agent.wrap_with_memory") as mock_wrap:
                mock_agent = MagicMock()
                mock_agent.invoke.return_value = {"output": "阿嬤早安！"}
                mock_wrap.return_value = mock_agent
                from agent.health_agent import build_agent, invoke_agent
                result = invoke_agent(build_agent(), "你好")
                assert isinstance(result, str)
                assert result == "阿嬤早安！"
```

- [ ] **Step 2: 執行測試確認失敗**

```bash
pytest tests/test_health_agent.py -v
```

預期：`ImportError: cannot import name 'build_agent'`

- [ ] **Step 3: 寫 agent/health_agent.py**

```python
# agent/health_agent.py
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent, AgentExecutor
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
```

- [ ] **Step 4: 執行全部測試確認通過**

```bash
pytest -v
```

預期：20 tests PASSED（含前面所有 task 的測試）

- [ ] **Step 5: Commit**

```bash
git add agent/health_agent.py tests/test_health_agent.py
git commit -m "feat(agent): 組裝 LangChain tool-calling agent 與 memory wrapper"
```

---

## Task 7: Streamlit 基礎 UI（Week 1 核心可跑）

**Files:**
- Create: `app.py`（基礎版：純對話，確認 agent 可正常運作）

- [ ] **Step 1: 寫 app.py 基礎版**

```python
# app.py
import streamlit as st
from dotenv import load_dotenv
from agent.health_agent import build_agent, invoke_agent

load_dotenv()

st.set_page_config(page_title="HomeWellness Companion", page_icon="🏥", layout="wide")
st.title("🏥 HomeWellness Companion")

if "agent" not in st.session_state:
    with st.spinner("載入 AI 健康伴侶中..."):
        st.session_state.agent = build_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("輸入訊息..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            response = invoke_agent(st.session_state.agent, user_input)
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

- [ ] **Step 2: 啟動並驗證基礎對話**

```bash
streamlit run app.py
```

在瀏覽器輸入：`我今天頭有點暈`

預期：Agent 呼叫 `get_vitals()`（terminal 顯示 verbose log），回應心率/血氧數值並給出建議。

- [ ] **Step 3: 驗證 Memory 連貫性**

輸入：`我叫陳阿嬤` → 再輸入：`你記得我叫什麼名字嗎？`

預期：Agent 正確回答「陳阿嬤」。

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(ui): 新增 Streamlit 基礎對話介面（Week 1 核心可跑）"
```

---

## Task 8: 左右分欄完整 UI + Demo 控制台

**Files:**
- Modify: `app.py`（完整版：左側數據面板 + 右側對話 + Demo 按鈕）

- [ ] **Step 1: 改寫 app.py 為左右分欄完整版**

```python
# app.py
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from agent.health_agent import build_agent, invoke_agent
from data.mock_sensors import (
    get_mock_vitals,
    get_mock_sleep_report,
    set_simulate_abnormal,
)

load_dotenv()

st.set_page_config(
    page_title="HomeWellness Companion",
    page_icon="🏥",
    layout="wide",
)

# ── Session State Init ────────────────────────────────
if "agent" not in st.session_state:
    with st.spinner("載入 AI 健康伴侶..."):
        st.session_state.agent = build_agent()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "simulate_abnormal" not in st.session_state:
    st.session_state.simulate_abnormal = False
if "pending_proactive" not in st.session_state:
    st.session_state.pending_proactive = None

# ── APScheduler Heartbeat ─────────────────────────────
from apscheduler.schedulers.background import BackgroundScheduler

if "scheduler_started" not in st.session_state:
    def _proactive_monitor():
        vitals = get_mock_vitals()
        thresholds = json.loads(
            Path("data/health_profile.json").read_text(encoding="utf-8")
        )["alert_thresholds"]
        if (
            vitals["heart_rate"] > thresholds["heart_rate_high"]
            or vitals["spo2"] < thresholds["spo2_low"]
        ):
            st.session_state["pending_proactive"] = (
                f"（系統觸發）偵測到異常數值：心率 {vitals['heart_rate']} bpm，"
                f"血氧 {vitals['spo2']}%，請立即關心陳阿嬤。"
            )

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_proactive_monitor, "interval", seconds=5)
    _scheduler.start()
    st.session_state.scheduler_started = True

# ── Handle Proactive Trigger ──────────────────────────
if st.session_state.pending_proactive:
    _msg = st.session_state.pending_proactive
    st.session_state.pending_proactive = None
    with st.spinner("Agent 偵測到異常..."):
        _resp = invoke_agent(st.session_state.agent, _msg)
    st.session_state.messages.append({"role": "assistant", "content": _resp})
    st.rerun()

# ── Layout ────────────────────────────────────────────
st.title("🏥 HomeWellness Companion")
col_data, col_chat = st.columns([1, 2])

# Left: Data Panel
with col_data:
    vitals = get_mock_vitals()
    sleep = get_mock_sleep_report()
    profile = json.loads(Path("data/health_profile.json").read_text(encoding="utf-8"))

    st.subheader("📊 即時生理數據")
    hr = vitals["heart_rate"]
    spo2 = vitals["spo2"]
    st.metric("💓 心率", f"{hr} bpm", "⚠️ 異常" if hr > 120 or hr < 50 else "正常")
    st.metric("🩸 血氧", f"{spo2}%", "⚠️ 異常" if spo2 < 90 else "正常")
    st.metric("😴 昨晚睡眠", f"{sleep['total_hours']} hrs")
    st.metric("🌡️ 環境溫度", f"{vitals['temperature']}°C")

    st.divider()
    st.subheader("💊 今日用藥")
    for med in profile["medications"]:
        st.write(f"⏰ {med['time']} — {med['name']}")

    st.divider()
    st.subheader("🎮 Demo 控制台")

    if st.button("🌅 模擬早晨問候", use_container_width=True):
        prompt = (
            "（系統觸發）現在是早上8點，請主動問候陳阿嬤，"
            "分享昨晚睡眠報告，並提醒早餐後服用降血壓藥。"
        )
        with st.spinner("Agent 思考中..."):
            response = invoke_agent(st.session_state.agent, prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🚨 模擬心率異常（125 bpm）", use_container_width=True):
        set_simulate_abnormal(True)
        st.session_state.simulate_abnormal = True
        prompt = (
            "（系統觸發）偵測到心率 125 bpm，血氧 88%，"
            "請立即關心陳阿嬤，並觸發緊急通報流程。"
        )
        with st.spinner("Agent 處理中..."):
            response = invoke_agent(st.session_state.agent, prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.session_state.simulate_abnormal:
        if st.button("🔄 恢復正常數值", use_container_width=True):
            set_simulate_abnormal(False)
            st.session_state.simulate_abnormal = False
            st.rerun()

# Right: Chat
with col_chat:
    st.subheader("💬 健康對話")
    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if user_input := st.chat_input("和阿嬤的健康伴侶說話..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("思考中..."):
            response = invoke_agent(st.session_state.agent, user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
```

- [ ] **Step 2: 手動驗證完整 UI**

```bash
streamlit run app.py
```

確認：
- 左側顯示四個生理數據 metric（含正常/異常 delta）
- 左側顯示三筆用藥記錄
- 左側有三個 Demo 按鈕
- 右側對話視窗正常運作

- [ ] **Step 3: 測試「模擬早晨問候」按鈕**

點擊「🌅 模擬早晨問候」。

預期：右側出現 Agent 主動問候，包含睡眠數據（呼叫 `get_sleep_report()`）與用藥提醒（呼叫 `get_medication_schedule()`）。

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(ui): 完成左右分欄 UI（數據面板 + 對話 + APScheduler 心跳）"
```

---

## Task 9: 四場景 Demo 最終驗證

**Files:**
- 無新檔案，驗證全部 Demo 場景可順利執行

- [ ] **Step 1: 場景 1 — 早安問候**

```bash
streamlit run app.py
```

點擊「🌅 模擬早晨問候」。

預期：Agent 說出問候，提及昨晚睡眠數據，提醒降血壓藥。terminal 顯示 `get_sleep_report` 與 `get_medication_schedule` 被呼叫。

- [ ] **Step 2: 場景 2 — 症狀 Tool Calling**

輸入：`我今天頭有點暈，感覺不太對`

預期：terminal 顯示 `get_vitals` 被呼叫，回應包含心率/血氧數值，語氣溫和給出建議。

- [ ] **Step 3: 場景 3 — 緊急通報**

點擊「🚨 模擬心率異常（125 bpm）」。

預期：
- 左側心率 metric 顯示 125 bpm + 「⚠️ 異常」
- terminal 印出 `[緊急通報] 已通報 陳大文（0912-345-678）...`
- 對話中出現通報確認訊息

- [ ] **Step 4: 場景 4 — 趨勢查詢**

輸入：`這週我的健康狀況怎麼樣？`

預期：terminal 顯示 `get_health_trend` 被呼叫（days=7），回應包含 7 日平均心率、血氧、睡眠數值與健康建議。

- [ ] **Step 5: 執行全部測試**

```bash
pytest -v --tb=short
```

預期：All PASSED（20 tests）

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "test: 四場景 Demo 驗證全部通過"
```

---

## Task 10: README + 最終文件

**Files:**
- Create: `README.md`

- [ ] **Step 1: 寫 README.md**

```markdown
# HomeWellness Companion — AI 健康伴侶 PoC

銀髮族主動式健康關懷 AI Agent，Technical PM (AI & IoT) 面試取回作業原型。

## 快速啟動

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定 API Key
cp .env.example .env
# 編輯 .env，填入 ANTHROPIC_API_KEY=sk-ant-...

# 3. 啟動
streamlit run app.py
```

## Live Demo 腳本（3 分鐘）

| 步驟 | 操作 | 展示重點 |
|------|------|---------|
| 1 | 點擊「🌅 模擬早晨問候」 | 主動觸發 + 長期記憶（姓名、病史） |
| 2 | 輸入「我今天頭有點暈」 | Tool Calling → get_vitals() |
| 3 | 點擊「🚨 模擬心率異常」 | 閾值觸發 → send_emergency_alert() |
| 4 | 輸入「這週健康狀況怎麼樣？」 | get_health_trend(7) + 記憶整合 |

## 技術架構

- **AI Agent**：LangChain `create_tool_calling_agent` + Claude claude-sonnet-4-6
- **Memory**：`RunnableWithMessageHistory` + `InMemoryChatMessageHistory`
- **Tools**：5 個工具（vitals / medication / sleep / trend / alert）
- **主動觸發**：APScheduler 背景心跳（每 5 秒輪詢感測數據）
- **UI**：Streamlit 左右分欄（數據面板 + 對話視窗）
- **工作流圖**：`langflow/workflow.json`（Langflow 視覺化導出）

## AWS 正式架構（簡報說明）

IoT 手環 → AWS IoT Core → Lambda → DynamoDB → API Gateway → Agent Service → SNS
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: 新增 README 快速啟動說明與 Demo 腳本"
```

---

## Task 11: Langflow 工作流（手動操作）

**目的**：產出 `langflow/workflow.json` 與截圖，放進簡報。

- [ ] **Step 1: 安裝並啟動 Langflow**

```bash
pip install langflow
python -m langflow run
```

瀏覽器開啟 `http://localhost:7860`

- [ ] **Step 2: 建立工作流**

依序拖拉元件並連線：

```
[Chat Input]
    ↓
[Claude claude-sonnet-4-6]  ←── [Prompt Template（system prompt）]
    ↓                                    ↑
[Agent（Tool Calling）]        [Memory（ConversationBufferMemory）]
    ↓
[Tool: get_vitals]
[Tool: get_medication_schedule]
[Tool: get_sleep_report]
[Tool: get_health_trend]
[Tool: send_emergency_alert]
    ↓
[Chat Output]
```

- [ ] **Step 3: 導出 JSON 並截圖**

右上角 → Export → 存為 `langflow/workflow.json`

截圖工作流存為 `langflow/workflow_screenshot.png`

- [ ] **Step 4: Commit**

```bash
git add langflow/
git commit -m "docs: 新增 Langflow AI 工作流 JSON 與截圖"
```

---

## 自我審查

**Spec 覆蓋確認：**

| 作業要求 | 對應 Task |
|---------|---------|
| User Journey | 設計文件 §7.1 |
| User Story + PRD | 設計文件 §7.2–7.4 |
| LangChain Agent | Task 6 |
| Memory（歷史 + 病史） | Task 5–6 |
| Tool Calling（IoT 數據） | Task 3 |
| 主動觸發（心跳） | Task 8（APScheduler） |
| 緊急通報 | Task 3（send_emergency_alert） |
| AWS 架構圖 | README + 簡報（口頭說明） |
| Streamlit Demo | Task 7–9 |
| Langflow JSON 導出 | Task 11 |
| GitHub repo | Task 1–11 全部 |

**無 TBD、無佔位符、所有 code block 均為完整可執行程式碼。**

---

*計畫版本：v1.0 — 2026-05-25*
