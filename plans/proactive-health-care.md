# Plan: 主動式健康關懷與用藥提醒

> Source PRD: docs/PRD.md

## Architectural Decisions

已確定的架構決策（跨 Phase 不變）：

- **Agent Framework**: LangChain 1.x `create_agent` → `CompiledStateGraph`
- **Multi-Agent Pattern**: CareAgent（主控）→ lazy import 子代理（AnalysisAgent、AlertAgent）
- **Memory**: `_AgentWithMemory` + `InMemoryChatMessageHistory`，session-scoped
- **IoT 輪詢**: APScheduler BackgroundScheduler，interval=5s，`pending_proactive` 機制
- **Tool 分配**: 最小權限原則（send_emergency_alert 只有 AlertAgent 持有）
- **資料格式**: `get_vitals()` 回傳 `dict`，含 `blood_pressure: {systolic, diastolic}`、`steps`；子代理回傳 `{"messages": [AIMessage]}`
- **UI**: Streamlit，左右分欄（資料面板 + 聊天）

---

## 現有程式碼對應（已完成的 Phase）

### ✅ Phase 0: 核心架構（已完成）

**對應程式碼**: `agent/`, `data/`, `app.py`

### What's built
- CareAgent 主對話 + 工具決策
- AnalysisAgent 深度趨勢分析（gemini-2.5-flash）
- AlertAgent 緊急數值評估 + 通報
- APScheduler 心跳 + pending_proactive 機制
- Streamlit 雙欄 UI + 場景模擬控制台
- 44 個 pytest 測試

### Acceptance criteria
- [x] `streamlit run app.py` 啟動無錯誤
- [x] 三個 Demo 按鈕可觸發（早晨問候 / 心率異常 / 自訂場景）
- [x] CareAgent 能呼叫全部 5 個工具
- [x] APScheduler 偵測異常後自動觸發 CareAgent
- [x] 44 tests pass（`pytest tests/ -v`）

---

## 待完成的 Phase（PoC 補強）

### [x] Phase 1: 感測器擴充（血壓 + 步數）

**User stories**: Story 3（症狀描述 → 數據讀取）、Story 5（緊急通報）

### What to build
在現有 mock_sensors 層加入血壓和步數。CareAgent 的 get_vitals tool 回傳完整的 5 個感測器數值，health_profile 加入血壓閾值。

### Acceptance criteria
- [x] `get_mock_vitals()` 回傳包含 `blood_pressure: {systolic, diastolic}` 和 `steps`
- [x] `health_profile.json` 新增 `systolic_high: 140, diastolic_high: 90`
- [x] `get_vitals` tool docstring 更新反映新欄位
- [x] `app.py` 資料面板顯示血壓和步數 metric
- [x] APScheduler 監控加入收縮壓 > 140 觸發條件
- [x] 場景模擬新增「高血壓」preset（systolic 168 / diastolic 108）
- [x] 10 個新 pytest 測試通過（共 44 個）

---

### [ ] Phase 2: 真實通知機制

**User stories**: Story 5（緊急通報）

### What to build
`send_emergency_alert` 從只輸出 log，改為真實發送通知。優先用 LINE Notify（免費、無需申請時間）。

### Acceptance criteria
- [ ] `send_emergency_alert(reason)` 發送 LINE Notify 訊息到家屬 LINE
- [ ] 訊息內容：時間 + 長者名 + 異常數值 + 原因
- [ ] 發送失敗不拋例外（return `{"error": "..."}` dict）
- [ ] LINE Token 存在 `.env`（不 commit）
- [ ] Demo 時：按下「模擬心率異常」後，手機確實收到 LINE 通知

---

### [ ] Phase 3: 效能可見性（Latency + Token Cost）

**User stories**: 技術架構評分（JD 第 5 點）

### What to build
在 Streamlit sidebar 加入即時效能儀表板，讓面試官看到 latency 和 token 使用量。

### Acceptance criteria
- [ ] 每次 `invoke_agent()` 計時，顯示 `上次回應延遲: X.Xs`
- [ ] sidebar 顯示累計 token 統計（input / output / total）
- [ ] sidebar 顯示累計 API 費用估算（USD）
- [ ] AnalysisAgent 呼叫有獨立計時
- [ ] 數值以 `st.metric` 顯示，異常延遲（>3s）顯示警告色

---

### [ ] Phase 4: 健康趨勢視覺化

**User stories**: Story 4（週健康趨勢）

### What to build
在 Streamlit 左側面板加入 30 天心率走勢折線圖，讓面試 Demo 有視覺衝擊力。

### Acceptance criteria
- [ ] 使用 Plotly 或 Altair 顯示 30 天心率平均折線圖
- [ ] 圖上標示閾值警戒線（120 bpm / 50 bpm）
- [ ] 異常點用不同顏色標注
- [ ] 圖表可互動（hover 顯示日期和數值）
- [ ] 加入血氧走勢（第二條線 or 分開的圖）

---

## 生產路線圖（超出 PoC 範圍）

```
Phase 5（Production Alpha）:
  - AWS IoT Core + Lambda 取代 APScheduler + mock_sensors
  - DynamoDB 取代 JSON 檔案
  - 真實 IoT 感測器 SDK 整合

Phase 6（Multi-user）:
  - User ID 系統
  - Redis session memory（取代 InMemory）
  - 家屬 Dashboard

Phase 7（Voice）:
  - STT/TTS 整合
  - 語音觸發主動對話
```
