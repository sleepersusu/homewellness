# HomeWellness Companion — 設計文件

**日期**：2026-05-25
**類型**：面試取回作業（Technical PM, AI & IoT）
**面試日**：約 2026-06-08
**評分維度**：技術架構 40% / Vibe Coding 30% / 產品知識 30%

---

## 1. 作業範圍

打造「主動式健康關懷與用藥提醒」功能的完整提案，包含：

- 產品設計：User Journey、User Story、PRD Snippet
- 技術架構：AWS 雲端架構圖 + LangChain AI Agent 工作流
- Vibe Coding 原型：可運行的 Streamlit chatbot demo（3–5 分鐘 Live Demo）
- 交付物：GitHub repo + Langflow workflow JSON + 簡報（PPT/PDF）

**Non-goals（MVP 範圍外）**：
- 語音輸入 / TTS 輸出
- 真實藥物資料庫整合
- 多用戶 / 家庭帳號管理
- 任何醫療診斷（僅提供建議）
- 真實 AWS 部署（架構圖 + 口頭說明即可）

---

## 2. 技術方案決策

### 選型：LangChain + Langflow + Streamlit（兩者都用）

| 工具 | 版本 | 用途 | 交付物 |
|------|------|------|--------|
| **langchain** | `>=0.3.0` | Agent / LCEL 編排 | GitHub repo |
| **langchain-anthropic** | `>=0.3.0` | Claude 整合 | — |
| **langchain-community** | `>=0.3.0` | 工具 / memory 擴充 | — |
| **anthropic** | `>=0.40.0` | Anthropic SDK | — |
| **streamlit** | `>=1.40.0` | Live Demo UI | 左右分欄 |
| **apscheduler** | `>=3.10.0` | 主動觸發排程（心跳機制） | — |
| **python-dotenv** | `>=1.0.0` | 環境變數管理 | `.env.example` |
| **Langflow** | `>=1.1.0`（本地安裝） | 視覺化工作流 | JSON 導出 + 截圖 |
| **Claude claude-sonnet-4-6** | — | LLM | Anthropic API |

> **LangChain 版本注意**：0.3.x 有破壞性改版。`ConversationBufferWindowMemory` 已 deprecated，記憶改用 `RunnableWithMessageHistory` + `InMemoryChatMessageHistory`；Agent 改用 `create_tool_calling_agent` + LCEL pipeline，棄用 `AgentExecutor`。

### requirements.txt

```txt
langchain>=0.3.0
langchain-anthropic>=0.3.0
langchain-community>=0.3.0
anthropic>=0.40.0
streamlit>=1.40.0
apscheduler>=3.10.0
python-dotenv>=1.0.0
```

Langflow 建在 LangChain 之上，不是互斥選項。Langflow 負責讓非技術評審看懂 Agent 設計，LangChain 負責讓技術評審看到真實程式碼能力。

---

## 3. 系統架構（四層）

```
Layer 1 — IoT 感測層（Demo 用 Mock 數據模擬）
  心率感測 / 睡眠品質 / 環境溫度 / 血氧濃度（SpO2）

         ↓ MQTT / AWS IoT Core

Layer 2 — AWS 雲端層（架構圖說明，不實際部署）
  AWS IoT Core → AWS Lambda → Amazon DynamoDB → Amazon API Gateway

         ↓ REST API

Layer 3 — AI Agent 層（LangChain 本地實作）
  LangChain AgentExecutor (Claude claude-sonnet-4-6)
    ├── Memory：短期（對話）+ 長期（健康檔案）
    └── Tools：get_vitals / get_medication_schedule / get_sleep_report
              / get_health_trend / send_emergency_alert

  Langflow：視覺化同一工作流，導出 JSON 交付

         ↓ 回應

Layer 4 — 使用者介面層
  Streamlit Web App（左側數據面板 + 右側對話視窗）
```

### AWS 數據流（簡報說明用）

```
IoT 手環
  → MQTT → AWS IoT Core（裝置連線管理）
  → IoT Rule 觸發 → AWS Lambda（數據處理、閾值判斷）
  → DynamoDB（健康記錄 + 用戶 Memory 持久化）
  → API Gateway → LangChain Agent Service（EC2 / ECS）
  → Anthropic Claude API
  → 回應推播至裝置 / 家屬 App（SNS）
```

---

## 4. AI Agent 設計

### 4.1 Memory 架構（兩層）

| 層級 | 實作（LangChain 0.3+） | 內容 |
|------|----------------------|------|
| **短期記憶** | `RunnableWithMessageHistory` + `InMemoryChatMessageHistory` | 最近 10 輪對話，存於 Streamlit `st.session_state` |
| **長期記憶** | `health_profile.json`（Demo）/ DynamoDB（正式） | 用戶姓名、慢性病史、用藥計畫、近 30 天生理數據趨勢 |

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

agent_with_memory = RunnableWithMessageHistory(
    agent,  # create_tool_calling_agent pipeline
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)
```

每次對話開始時，長期記憶（健康檔案）以 system prompt injection 方式注入，讓 Agent 知道用戶身份與病史。

### 4.2 Tools 定義（5 個）與 Agent 建立

```python
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

@tool
def get_vitals() -> dict:
    """讀取即時生理數據：心率、血氧、體溫。
    觸發時機：用戶提及身體不適（「頭暈」、「不舒服」）"""

@tool
def get_medication_schedule() -> dict:
    """查詢今日用藥計畫（藥名、時間、劑量）。
    觸發時機：定時提醒或用戶詢問用藥"""

@tool
def get_sleep_report() -> dict:
    """回傳昨晚睡眠品質、深眠時長、起夜次數。
    觸發時機：早晨問候時主動分享"""

@tool
def get_health_trend(days: int = 7) -> dict:
    """分析近 N 天生理數據趨勢，偵測異常模式。
    觸發時機：用戶詢問近期健康狀況"""

@tool
def send_emergency_alert(reason: str) -> str:
    """偵測到異常數值時通報家屬及診所。
    觸發條件：心率 < 50 或 > 120，血氧 < 90%"""

# Agent 建立（LangChain 0.3+ 推薦寫法）
llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
tools = [get_vitals, get_medication_schedule, get_sleep_report,
         get_health_trend, send_emergency_alert]

prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),       # 注入長期記憶 + 語氣設計
    MessagesPlaceholder("chat_history"), # 短期記憶
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

### 4.3 主動觸發邏輯（心跳機制）

主動式 Agent 的本質是**背景心跳排程**：APScheduler 在背景執行緒定時檢查條件，條件成立時寫入 `st.session_state`，Streamlit 偵測到狀態變化後 `st.rerun()` 顯示 Agent 主動發出的訊息。

```python
from apscheduler.schedulers.background import BackgroundScheduler

def proactive_check():
    vitals = get_mock_vitals()
    # 閾值異常：寫入待推送訊息佇列
    if vitals["heart_rate"] > 120 or vitals["spo2"] < 90:
        st.session_state["pending_alert"] = f"偵測到異常：心率 {vitals['heart_rate']} bpm"

scheduler = BackgroundScheduler()
scheduler.add_job(proactive_check, "interval", seconds=5)   # 數據監控（每 5 秒）
scheduler.add_job(morning_greeting,  "cron", hour=8, minute=0)  # 早安問候
scheduler.add_job(med_reminder,      "cron", hour=13, minute=0) # 用藥提醒
scheduler.start()
```

| 觸發類型 | 實作 | Agent 行為 |
|---------|------|-----------|
| **定時觸發** | APScheduler `cron` job（08:00 / 13:00 / 21:00） | 早安問候、午間用藥提醒、晚安關懷 |
| **數據異常觸發** | APScheduler `interval` job（每 5 秒輪詢） | 呼叫 `get_vitals()` + 評估是否通報 |
| **對話意圖觸發** | Agent 推論用戶輸入意圖 | Tool Calling → 呼叫對應工具 |

> Demo 簡化：面試當下用 Streamlit sidebar 的「模擬早晨」、「模擬異常心率」按鈕手動觸發，避免等待真實時間點。

### 4.4 語氣設計（Vibe）— System Prompt 原則

```
你是陳阿嬤的健康伴侶，像一個關心她的晚輩。

語氣規則：
- 稱呼她的名字，不說「用戶」
- 每次只傳達一件事，句子不超過 2 行
- 用鼓勵取代警告（「喝點水看看」而非「你可能脫水了」）
- 引用她上次說的話，讓對話有連貫感
- 繁體中文，避免醫療術語
- 遇到異常數值：先安撫，再說明，最後問是否需要幫忙
```

---

## 5. Streamlit UI 設計

**版型**：左右分欄（方案 A）

```
┌─────────────────────────────────────────────────┐
│  HomeWellness Companion                         │
├──────────────────┬──────────────────────────────┤
│  📊 生理數據      │  💬 健康對話                  │
│                  │                              │
│  💓 心率  72bpm  │  [Agent] 阿嬤早安！昨晚睡了   │
│  🩸 血氧  97%    │  6.5小時，睡眠品質不錯喔。    │
│  😴 睡眠  6.5h   │  今天記得吃降血壓藥 😊        │
│  🌡️ 溫度  26°C   │                              │
│                  │  [User] 我今天頭有點暈...      │
│  💊 今日用藥      │                              │
│  ─────────────   │  [Agent] 我幫您確認一下...    │
│  ✅ 降血壓藥 8:00 │  心率72、血氧97%，都正常。    │
│  ⏳ 維生素D 13:00 │  先喝一杯溫水看看 💧          │
│                  │                              │
│                  │  ┌──────────────────┐ [送出] │
└──────────────────┴──────────────────────────────┘
```

左側數據面板每 5 秒刷新（`st.rerun()`），讓面試官看到數據動態更新與 Agent 回應的視覺連動。

---

## 6. 專案檔案結構

```
homewellness/
├── app.py                      # Streamlit 主程式（UI 入口）
├── agent/
│   ├── health_agent.py         # LangChain AgentExecutor 設定
│   ├── tools.py                # 5 個 @tool 工具定義
│   ├── memory.py               # 短期 + 長期記憶管理
│   └── prompts.py              # System prompt（語氣設計）
├── data/
│   ├── mock_sensors.py         # 模擬即時 IoT 數據
│   ├── health_profile.json     # 長者健康檔案（用藥、病史）
│   └── health_history.json     # 近 30 天生理數據記錄
├── langflow/
│   ├── workflow.json           # Langflow 導出的工作流檔案
│   └── workflow_screenshot.png # 工作流截圖（放進簡報）
├── docs/
│   ├── aws_architecture.png    # AWS 架構圖
│   ├── user_journey.md         # User Journey 說明
│   └── prd_snippet.md          # PRD 核心段落
├── .env.example                # ANTHROPIC_API_KEY 等環境變數
├── requirements.txt
└── README.md                   # 一鍵啟動 + Demo 腳本
```

---

## 7. 產品設計

### 7.1 核心 User Journey

| 步驟 | 發生什麼 | 技術觸發 |
|------|---------|---------|
| 1. 感知 | IoT 偵測起床心率數據 | AWS IoT Core 收到 MQTT |
| 2. 判斷 | Agent 讀取健康檔案、比對昨日數據 | Lambda + DynamoDB |
| 3. 主動問候 | Agent 說出個人化早安問候 | System prompt + sleep report |
| 4. 互動回應 | 長者說「頭暈」，Agent 觸發工具 | `get_vitals()` |
| 5. 健康行動 | 給建議、提醒用藥、更新記憶 | Memory 寫回 |
| 6. 緊急通報 | 若數值異常，通報家屬 | `send_emergency_alert()` + SNS |

### 7.2 核心 User Stories

**US-01 主動問候**
身為銀髮用戶，我希望每天早上能收到 AI 的個人化問候與健康摘要，讓我感覺被關心，而不是面對冰冷的機器。

**US-02 用藥提醒**
身為有慢性病的用戶，我希望在每次服藥時間前收到溫柔提醒，確認後記錄已服藥，避免漏藥或重複服藥。

**US-03 症狀查詢**
身為用戶，當我說「我今天不舒服」時，AI 能主動讀取我的生理數據，並用我能理解的語言給出具體建議（而非醫療診斷）。

**US-04 緊急通報**
身為家屬，當長輩的生理數據出現異常時，我希望立即收到通知，並了解當時的對話情境與數據。

### 7.3 US-03 驗收條件

- 用戶提及身體不適 → 3 秒內觸發 `get_vitals()`
- 回應語言為繁體中文，每則訊息 ≤ 2 行
- 數值正常 → 給出生活建議（喝水、休息）
- 數值異常 → 告知情況並詢問是否通報家屬
- 本次對話與數據寫入長期記憶

### 7.4 成功指標

| 指標 | 目標值 |
|------|--------|
| 用藥提醒確認率 | ≥ 80% |
| 異常偵測 → 通報延遲 | < 30 秒 |
| 用戶每日主動對話 | ≥ 1 次 |

---

## 8. Live Demo 腳本（3 分鐘）

| 場景 | 操作 | 展示重點 | 時長 |
|------|------|---------|------|
| 1. 早安問候 | 點擊「模擬早晨」 | 主動觸發 + 長期記憶（知道姓名、病史） | 45s |
| 2. 說「頭暈」 | 輸入「我今天頭有點暈」 | Tool Calling + 即時數據讀取 | 50s |
| 3. 緊急通報 | 點擊「模擬心率異常（125bpm）」| 閾值觸發 + send_emergency_alert() | 40s |
| 4. 趨勢查詢 | 輸入「這週健康狀況怎麼樣？」 | get_health_trend() + 記憶整合 | 45s |

---

## 9. 實作優先順序

**Week 1（核心可跑）**
1. `data/` — mock sensor 數據 + health profile JSON
2. `agent/tools.py` — 5 個工具（先用 mock 數據）
3. `agent/prompts.py` — system prompt 語氣設計
4. `agent/health_agent.py` — AgentExecutor 組裝
5. `app.py` — Streamlit 基本 UI 可對話

**Week 2（完整打磨）**
1. `agent/memory.py` — 長期記憶注入
2. Streamlit UI 左右分欄 + 數據刷新
3. Demo 場景 3（心率異常觸發）
4. Langflow 工作流繪製 + JSON 導出
5. `docs/` — AWS 架構圖 + PRD Snippet
6. README + `.env.example` + 簡報

---

*設計文件版本：v1.0 — 2026-05-25*
