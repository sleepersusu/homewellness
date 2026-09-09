# HomeWellness Companion

> 主動感知、溫暖開口的 AI 健康伴侶——為獨居長者設計，整合 IoT 感測、Multi-Agent 協調與 Proactive Trigger。

*[English README](README.md)*

---

## 一句話說明

`st.fragment(run_every=5s)` 每 5 秒輪詢 IoT 生理數據，偵測異常（心率、血氧、血壓）後自動觸發 CareAgent 主動發起對話；長者也可以隨時直接輸入症狀，AI 即時讀取數值並給出回應。

---

## 快速啟動

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定 API Key
cp .env.example .env
# 在 .env 填入 OPENAI_API_KEY 和 GOOGLE_API_KEY

# 3. 啟動
streamlit run app.py
```

開啟瀏覽器 `http://localhost:8501`

---

## Live Demo 腳本（3 分鐘）

| 步驟 | 操作 | 展示重點 |
|------|------|---------|
| 1 | 點擊「🌅 模擬早晨問候」 | Proactive Trigger + session 記憶（姓名、病史、用藥）|
| 2 | 輸入「我今天頭有點暈」 | Tool Calling → `get_vitals()` 讀取即時血壓 / 心率 / 血氧 |
| 3 | 場景切「心跳過快」→ 等 5 秒 | st.fragment 閾值觸發 → AlertAgent → `send_emergency_alert()` |
| 4 | 輸入「這週健康狀況怎麼樣？」 | CareAgent 委派 → AnalysisAgent → `get_health_trend(7)` |
| 5 | 場景切「高血壓」→ 等 5 秒 | 收縮壓 > 140 mmHg 觸發主動關懷流程 |

---

## 功能特色

| 功能 | 說明 |
|------|------|
| **主動觸發** | 心率 > 120 bpm、血氧 < 90%、收縮壓 > 140 mmHg → 10 秒內 CareAgent 主動開口 |
| **Multi-Agent 協調** | CareAgent 主控，視情況委派 AnalysisAgent（趨勢）或 AlertAgent（緊急）|
| **即時生理監測** | 心率 / 血氧 / 血壓 / 步數 / 體溫，5 種預設場景（正常 / 心跳過快 / 心跳過慢 / 低血氧 / 高血壓）+ 自訂滑桿模式 |
| **Session 記憶** | 對話中不重複詢問，`_AgentWithMemory` 保持上下文連貫 |
| **語氣設計** | 貼心晚輩口吻，用名字（阿嬤），不作醫療診斷，每則訊息只說一件事 |
| **模型可切換** | Sidebar 即時選擇每個 Agent 的 LLM（OpenAI / Gemini），不需重啟 |
| **效能監控** | Sidebar 即時顯示每次回應延遲、Token 用量、費用估算與累計統計 |
| **Agent 自排程追蹤** | AlertAgent 通報後自動呼叫 `schedule_followup`，N 分鐘後主動追蹤確認（cron-as-tool）|
| **30 天趨勢儀表板** | 獨立 Tab：心率 / 血氧 / 收縮壓折線圖 + 警報閾值虛線 + vs 昨日 delta |

---

## 系統架構

```
IoT 感測器（mock_sensors.py）
  └─ st.fragment 每 5 秒輪詢（主執行緒，無 threading 問題）
       ├─ 正常 → 繼續輪詢
       └─ 異常 → pending_proactive → st.rerun()
                    ↓
            CareAgent（gpt-4o-mini）— 主控 Orchestrator
              ├─ 工具：get_vitals / get_sleep_report / get_medication_schedule
              ├─ 趨勢問題 → AnalysisAgent（gemini-2.5-flash）→ get_health_trend(N)
              └─ 數值異常 → AlertAgent（gpt-4o-mini）→ send_emergency_alert(reason)
                                  └─ schedule_followup(reason) → threading.Timer
                                       └─ N 分鐘後重入 pending_proactive（追蹤確認）
```

**AWS 生產架構對應：**

| 生產環境 | PoC 對應 |
|---------|---------|
| AWS IoT Core（MQTT/TLS）| `mock_sensors.py` |
| Lambda `anomaly-detector` | st.fragment 閾值判斷 |
| Lambda `data-ingester` | — |
| DynamoDB `health_events` | `health_history.json` |
| ECS Fargate（LangChain）| `streamlit run app.py` |
| AWS SNS | `send_emergency_alert()`（目前 log 輸出）|

詳細架構說明見 [`docs/PRD.md`](docs/PRD.md) §8。

---

## 目錄結構

```
homewellness/
├── app.py                    # Streamlit UI + st.fragment 心跳監測
├── charts.py                 # Plotly 30 天健康趨勢圖（build_trend_chart）
├── agent/
│   ├── health_agent.py       # CareAgent（主控 orchestrator）+ token / 費用統計
│   ├── analysis_agent.py     # AnalysisAgent（深度趨勢分析）
│   ├── alert_agent.py        # AlertAgent（緊急評估與通報）
│   ├── llm_factory.py        # LLM 工廠：OpenAI / Gemini 統一介面
│   ├── tools.py              # 6 個 @tool 工具（最小權限原則）
│   ├── prompts.py            # 3 個 build_*_prompt()，動態注入病患資料
│   ├── memory.py             # _AgentWithMemory + InMemoryChatMessageHistory
│   └── scheduler_tools.py    # followup 佇列 + Timer 自排程（cron-as-tool）
├── data/
│   ├── mock_sensors.py       # Mock IoT（心率 / 血氧 / 血壓 / 步數 / 體溫）
│   ├── health_profile.json   # 病患靜態資料（陳阿嬤）+ 警報閾值
│   └── health_history.json   # 近 30 天生理歷史
├── tests/                    # 63 個 pytest 測試，共 9 個模組
│   ├── conftest.py           # autouse fixture：每個測試前後清空 session 記憶
│   ├── test_health_agent.py  · test_analysis_agent.py · test_alert_agent.py
│   ├── test_tools.py         · test_prompts.py        · test_memory.py
│   └── test_mock_sensors.py  · test_scheduler_tools.py · test_charts.py
├── docs/
│   ├── PRD.md                # 產品需求文件（User Journey / User Stories / 成功指標）
│   ├── story.md              # 〈陳阿嬤的一天〉產品敘事
│   ├── HomeWellness_Proactive_AI (1).pdf  # 簡報投影片
│   └── superpowers/          # 設計規格與實作計畫（歷史紀錄）
├── CLAUDE.md / AGENTS.md     # 本 repo 的 coding agent 指引
├── pytest.ini
├── .env.example
└── requirements.txt
```

---

## 警報閾值

所有閾值都寫在 `data/health_profile.json` 的 `alert_thresholds`，app 與 agent 一律從此讀取，程式碼不硬寫數字。

| 指標 | 警報條件 |
|------|---------|
| 心率 | < 50 bpm 或 > 120 bpm |
| 血氧（SpO2）| < 90% |
| 收縮壓 | > 140 mmHg |
| 舒張壓 | > 90 mmHg |

任一項越界即寫入 `pending_proactive`，下一次 rerun 由 CareAgent 主動開口。

---

## 執行測試

```bash
# 全部測試（63 個）
pytest tests/ -v

# 含覆蓋率報告
pytest tests/ --cov=agent --cov=data --cov-report=term-missing
```

---

## 環境變數

```env
OPENAI_API_KEY=sk-...      # CareAgent + AlertAgent（gpt-4o-mini）
GOOGLE_API_KEY=...         # AnalysisAgent（gemini-2.5-flash）
```

模型在 Streamlit sidebar 即時切換，不需重啟。

---

## 設計原則

- **最小權限**：`send_emergency_alert` 只授予 AlertAgent；`get_health_trend` 只授予 AnalysisAgent
- **語氣設計**：每則訊息只說一件事，用名字不用「用戶」，不作醫療診斷
- **Lazy Import**：AnalysisAgent / AlertAgent 在 `build_agent()` 函式體內 import，防止循環 import
- **不使用** `RunnableWithMessageHistory`（已 deprecated），改用自建 `_AgentWithMemory`
- **Cron-as-tool**：`schedule_followup` 讓 AlertAgent 自排程後續追蹤，不依賴外部 cron，Agent 掌控自己的時間軸

---

## 文件

| 文件 | 內容 |
|------|------|
| [`docs/PRD.md`](docs/PRD.md) | 產品需求文件：問題與機會、使用者、User Journey、User Stories、功能需求、Non-Goals、成功指標、AWS 生產架構對應、Demo 腳本 |
| [`docs/story.md`](docs/story.md) | 〈陳阿嬤的一天〉——設計決策背後的產品敘事 |
| `docs/HomeWellness_Proactive_AI (1).pdf` | 簡報投影片 |
| [`docs/superpowers/`](docs/superpowers) | 原始設計規格與實作計畫，保留為歷史紀錄（早於目前架構） |

---

## 適用範圍與限制

這是一個 **PoC**，作為 Technical PM（AI & IoT）職缺的取回作業原型。明確說明哪些是真的、哪些不是：

- **感測器是模擬的**：`data/mock_sensors.py` 產生生理數值，沒有接實體裝置或 MQTT broker。生產路徑（AWS IoT Core → Lambda → DynamoDB）有設計但未實作。
- **通報只寫 log，沒有真的發出去**：`send_emergency_alert()` 輸出到 log，沒有接 SNS、簡訊或電話。
- **未經臨床驗證**：閾值取自常見參考範圍，不是經驗證的臨床準則；Agent 的 prompt 明確禁止做醫療診斷。
- **單一病患、單一 session**：記憶存在行程內（`InMemoryChatMessageHistory`），重啟即消失；沒有資料庫、認證或多租戶。
- **LLM 行為未做基準測試**：延遲、token、費用在 sidebar 即時量測，但沒有離線 eval set 來評估回應品質或誤報率。
