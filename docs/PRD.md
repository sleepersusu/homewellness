# HomeWellness Companion — Product Requirements Document

**版本**：v2.0  
**角色**：Technical PM (AI & IoT) 面試取回作業  
**日期**：2026-06-12  
**範圍**：主動式健康關懷與用藥提醒——PoC 原型

---

## 1. 問題與機會

### 問題陳述

台灣獨居長者超過 90 萬人，慢性病管理與緊急通報高度依賴家屬主動聯繫。現有解法（Line 群組、定時提醒 App）屬於**被動式**——長者需主動開口或按按鈕，但認知退化與獨立心態往往讓求助行為滯後，錯失黃金處理時間。

### 核心洞察

長者需要的不是「工具」，而是**一個感覺真心關心自己的存在**：

- 主動問候，不等長者開口
- 說的是白話，不是醫療術語
- 記得她上次說過的事
- 出事了立刻通知家人

### 機會

IoT 感測器（心率、血氧、血壓）+ Multi-Agent LLM 的結合，可以實現**「感知 → 判斷 → 主動開口」**的閉環，把被動守護升級為主動陪伴。

---

## 2. 使用者

### 主要用戶：獨居長者（陳阿嬤，72 歲）

| 屬性 | 說明 |
|------|------|
| 慢性病史 | 高血壓、輕度糖尿病 |
| 用藥 | Amlodipine（08:00）、維生素D（13:00）、Metformin（19:00） |
| 科技能力 | 會用 Line，打字慢，不喜歡複雜介面 |
| 核心痛點 | 不想麻煩家人，但身體出狀況時不知道找誰說 |

### 次要用戶：家屬（陳大文，長者之子）

- 需要在無法親自陪伴時，確保長者安全
- 希望異常時立即收到通知，並了解當時情境

---

## 3. User Journey

| 步驟 | 觸發 | 系統行為 | 技術實作 |
|------|------|---------|---------|
| 1. **感知** | IoT 感測器偵測起床後心率數據 | 持續監測五項生命體徵 | `st.fragment(run_every=5s)` 輪詢 `mock_sensors.py` |
| 2. **判斷** | 與警報閾值比對 | 評估是否觸發主動問候或緊急通報 | CareAgent 決策樹 |
| 3. **主動問候** | 早上 8 點（或異常偵測） | Agent 主動說出個人化問候 | System prompt 注入健康檔案 |
| 4. **互動回應** | 長者說「頭暈」 | 即時讀取生理數據，溫和給出建議 | `get_vitals()` Tool Calling |
| 5. **深度分析** | 長者問「這週健康怎樣？」 | 7-30 天趨勢分析，結構化摘要 | AnalysisAgent + `get_health_trend()` |
| 6. **緊急通報** | 數值超過警報閾值 | 評估、通報家屬、排程追蹤確認 | AlertAgent → `send_emergency_alert()` → `schedule_followup()` |

---

## 4. User Stories

### US-01 主動問候（早晨）

> 身為獨居長者，我希望每天早上收到 AI 主動問候與前一晚睡眠報告，讓我感覺被關心，而不是盯著空白螢幕等待。

**驗收條件：**
- 早上 8 點系統自動觸發，無需長者操作
- 問候包含昨晚睡眠數據（總時數、深眠時長）
- 提醒早餐後服藥，語氣為鼓勵非警告
- 全程繁體中文，每則訊息不超過 2 行

---

### US-02 用藥提醒

> 身為有慢性病的長者，我希望每次服藥前收到溫柔提醒，確認後記錄已服藥，避免漏藥。

**驗收條件：**
- 按用藥計畫時間觸發提醒（08:00 / 13:00 / 19:00）
- 長者可調整用藥時間（UI 支援）
- 提醒說明藥名與服用方式（隨餐 / 空腹）

---

### US-03 症狀查詢

> 身為長者，當我說「我今天不舒服」，AI 能主動讀取生理數據，用我聽得懂的話給出具體建議（不是醫療診斷）。

**驗收條件：**
- 偵測到身體不適關鍵字 → 3 秒內觸發 `get_vitals()`
- 數值正常 → 給出生活建議（喝水、休息）
- 數值異常 → 先確認是情緒表達還是生理緊急，再決定是否通報
- 不重複說「我已通報陳大文」——通報後改為陪伴模式

---

### US-04 緊急通報

> 身為家屬，當長輩生理數據出現危險異常時，我希望立即收到通知，並了解當時的數值與對話情境。

**驗收條件：**

| 指標 | 警報條件 |
|------|---------|
| 心率 | < 50 bpm 或 > 120 bpm |
| 血氧（SpO2）| < 90% |
| 收縮壓 | > 140 mmHg |
| 舒張壓 | > 90 mmHg |

- 符合條件 → AlertAgent 評估 → `send_emergency_alert()` 通報陳大文
- 通報後 N 分鐘自動追蹤確認（N 由 sidebar 設定，預設 30 分鐘）
- 同一異常組合 60 秒內不重複通報（防止 spam）
- 異常類型改變時立即重新觸發

---

### US-05 健康趨勢查詢

> 身為長者，我希望能問 AI「我這週身體怎麼樣」，得到一個看得懂的健康摘要。

**驗收條件：**
- 偵測趨勢查詢意圖 → CareAgent 委派 AnalysisAgent
- AnalysisAgent 分析 7-30 天心率、血氧、血壓、睡眠數據
- 回傳結構化摘要：趨勢方向、異常點、具體建議（3-5 行）
- CareAgent 以長者友善語氣呈現分析結果

---

## 5. 功能需求

### 5.1 Multi-Agent 架構

| Agent | 模型 | 職責 | 工具 |
|-------|------|------|------|
| **CareAgent** | gpt-4o-mini | 主控對話、決策委派 | `get_vitals` / `get_sleep_report` / `get_medication_schedule` / `call_analysis_agent` / `call_alert_agent` |
| **AnalysisAgent** | gemini-2.5-flash | 深度健康趨勢分析 | `get_health_trend` |
| **AlertAgent** | gpt-4o-mini | 緊急評估與通報 | `get_vitals` / `send_emergency_alert` / `schedule_followup` |

**設計原則：** 最小權限——`send_emergency_alert` 只授予 AlertAgent，`get_health_trend` 只授予 AnalysisAgent。

### 5.2 主動觸發機制

```
st.fragment(run_every=5s)
  → 偵測閾值異常
    → 異常類型比對（防重複）
      → st.session_state["pending_proactive"] = "系統觸發訊息"
        → st.rerun() → CareAgent 主動開口
```

相較 APScheduler（背景執行緒）的優勢：主執行緒運行，無 thread-safety 問題，Streamlit 原生支援。

### 5.3 Session 記憶

- 短期記憶：`_AgentWithMemory` + `InMemoryChatMessageHistory`（per session）
- 長期記憶：`health_profile.json` 於每次對話注入 system prompt（姓名、病史、用藥、閾值）

### 5.4 Streamlit UI

- 左側面板：即時生理數據（5 項）、用藥計畫、場景模擬、Demo 控制台
- 右側面板：健康對話視窗
- Sidebar：模型選擇、效能監控（延遲 / Token / 費用）、追蹤間隔設定
- 趨勢 Tab：30 天生理數據折線圖（Plotly），含警報閾值虛線

---

## 6. Non-Goals（MVP 範圍外）

- 語音輸入 / TTS 輸出
- 真實藥物資料庫整合
- 多用戶 / 家庭帳號管理
- 任何醫療診斷（僅提供生活建議）
- 真實 AWS 部署（架構圖 + 口頭說明即可）
- 真實 IoT 裝置整合（Mock 數據模擬）
- 真實 SNS 發送（log 輸出模擬）

---

## 7. 成功指標

| 指標 | PoC 目標 | 正式產品目標 |
|------|---------|------------|
| 異常偵測 → 通報延遲 | < 10 秒 | < 30 秒 |
| 用藥提醒確認率 | Demo 可展示 | ≥ 80% |
| 長者每日主動對話 | — | ≥ 1 次 |
| 誤報率（正常誤判為異常） | — | < 5% |
| Agent 回應延遲 | < 5 秒（gpt-4o-mini） | < 3 秒 |

---

## 8. AWS 生產架構對應

| PoC 實作 | 生產環境替換 |
|---------|------------|
| `mock_sensors.py` | AWS IoT Core（MQTT/TLS）+ IoT 手環 |
| `st.fragment` 閾值判斷 | Lambda `anomaly-detector` |
| `health_history.json` | DynamoDB `health_events` |
| `streamlit run app.py` | ECS Fargate（LangChain Agent Service）|
| `send_emergency_alert()`（log 輸出）| AWS SNS → 家屬 App 推播 |
| `InMemoryChatMessageHistory` | DynamoDB（對話記憶持久化）|

---

## 9. Live Demo 腳本（3 分鐘）

| # | 操作 | 展示重點 | 預期時長 |
|---|------|---------|---------|
| 1 | 點擊「🌅 模擬早晨問候」 | 主動觸發 + 長期記憶（知道病史、用藥） | 45s |
| 2 | 輸入「我今天頭有點暈」 | Tool Calling → `get_vitals()`，數值即時讀取 | 45s |
| 3 | 場景切「心跳過快」→ 等 5 秒 | st.fragment 自動偵測 → AlertAgent → 緊急通報 | 40s |
| 4 | 輸入「這週健康狀況怎麼樣？」 | CareAgent 委派 AnalysisAgent → 趨勢摘要 | 50s |

---

*PRD 版本：v2.0 — 2026-06-12*
