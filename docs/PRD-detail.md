# HomeWellness Companion — 主動式健康關懷與用藥提醒
## Product Requirements Document (PRD)

**版本：** v1.0  
**狀態：** Draft  
**作者：** Technical PM Candidate  
**日期：** 2026-05-26  
**類型：** Take-home Assignment — Technical PM (AI & IoT)

---

## 1. Executive Summary

我們正在為獨居銀髮族與亞健康族群打造 **HomeWellness Companion**——一款結合 IoT 生理感測器與多代理 AI 系統的主動式居家健康裝置。

**核心功能：** 主動式健康關懷與用藥提醒

> 「我們正在為像陳阿嬤一樣獨居的 72 歲長者，解決子女不在身邊時的健康盲區問題。系統每 5 秒輪詢 IoT 生理數據，偵測異常時主動發起對話、觸發緊急通報，讓家屬從『我希望媽媽平安』變成『我知道媽媽現在很好』。」

**商業影響預期：**
- 異常偵測到通報時間：從數小時 → 10 秒以內
- 家屬焦慮指標（主觀評分）：目標降低 40%
- 用藥遵從率：目標從 ~60% 提升至 85%+

---

## 2. Problem Statement

### 誰有這個問題？
台灣獨居長者（65 歲以上），及其無法全天候陪伴的成年子女或主要照顧者。

### 問題是什麼？
**長者側：** 慢性病（高血壓、糖尿病）的生理異常往往無聲無息。長者不知道自己的心率正在飆升，等到症狀明顯已錯過黃金處置時間。

**家屬側：** 只能在特定時段打電話，其餘時間完全是黑盒子。「打電話媽媽說沒事，但我不知道她今天心跳幾下、血氧多少。」

### 為什麼痛？

| 影響面 | 具體痛點 |
|--------|---------|
| 長者健康 | 心臟驟停、低血氧等緊急事件平均發現延遲 > 2 小時（獨居場景） |
| 家屬心理 | 持續性照顧焦慮，無法安心工作 |
| 醫療體系 | 可預防的急診住院，增加醫療資源負擔 |
| 用藥管理 | 長者自述忘記服藥比例達 40%（慢性病管理研究，2024） |

### 假設與待驗證假說
> **注：** 以下為產品假說，PoC 階段以 mock 數據模擬，正式上線前需真實用戶研究驗證。

- 假說 1：長者對 AI 語音伴侶的接受度，在「溫暖語氣」設計下 > 70%（vs. 冰冷警報系統）
- 假說 2：主動問候觸發的對話，比被動詢問更能讓長者揭露真實身體狀況
- 假說 3：家屬每日收到 1 次健康摘要，焦慮指數顯著下降

---

## 3. Target Users & Personas

### 主要使用者：陳阿嬤型（設備穿戴者）

| 屬性 | 描述 |
|------|------|
| 年齡 | 65–80 歲 |
| 居住 | 獨居或白天獨處 |
| 慢性病 | 高血壓、糖尿病、心臟病其中一種以上 |
| 科技熟悉度 | 低（使用 LINE，但不使用 App） |
| 核心需求（JTBD） | 「我想知道自己今天狀況好不好，不需要自己判斷。」 |
| 信任模型 | 把 AI 當成「貼心晚輩」，接受建議但不接受命令 |
| 恐懼 | 成為家人的負擔；自己出事沒人知道 |

### 次要使用者：陳大文型（遠端照顧者）

| 屬性 | 描述 |
|------|------|
| 年齡 | 40–55 歲 |
| 關係 | 子女或主要照顧者 |
| 工作狀態 | 全職上班，無法 24 小時監控 |
| 核心需求（JTBD） | 「我想要在媽媽真的需要幫助時第一個知道，其他時候不要打擾我。」 |
| 信任模型 | 需要數據佐證，不接受「AI 說沒事就沒事」 |
| 恐懼 | 錯過緊急事件；過多假警報導致麻木 |

### AI 信任邊界（重要設計原則）

```
長者信任層：
  AI 可做 → 提醒、問候、建議、陪伴對話
  AI 不可做 → 醫療診斷、決定是否就醫（AI 建議，人類決定）

家屬信任層：
  AI 可做 → 異常通報、健康摘要、趨勢數據
  AI 不可做 → 替代醫生判斷、保證健康狀態
```

---

## 4. Strategic Context

### 商業目標連結
| OKR 層級 | 目標 |
|---------|------|
| 公司 | 成為台灣銀髮 AI 照護市場領導者（3 年內） |
| 產品線 | HomeWellness Companion 首年觸達 10,000 台裝置 |
| 本功能 | 主動關懷功能是核心差異化，驅動留存與口碑（NPS 目標 > 50） |

### 市場機會
- **TAM：** 全球銀髮科技市場，2030 年預計 $2.8 兆美元
- **SAM：** 台灣 65 歲以上人口 420 萬（2025），獨居約 85 萬人
- **SOM：** 首階段鎖定有慢性病的獨居長者，約 30 萬人；滲透率 3% = 9,000 用戶

### 競爭格局

| 競品 | 強項 | 弱點 |
|------|------|------|
| Apple Watch | 品牌信任度高 | 操作複雜；長者接受度低 |
| 純感測器腕帶（小米等） | 便宜 | 無 AI，只有被動警報 |
| 傳統緊急鈕（Life Alert） | 長者熟悉 | 被動式；需長者自己按 |
| **HomeWellness（本產品）** | **主動感知 + 溫暖 AI 對話** | **PoC 階段，數據需驗證** |

### 為什麼是現在？
- LLM API 成本在 2024–2025 年下降 80%，消費級 AI 伴侶首次可行
- 台灣超高齡社會（2025 正式進入）政策紅利
- 多代理框架（LangChain）成熟，TPM 可直接 Vibe Code 出可運作 PoC

---

## 5. Solution Overview

### 系統行為模式

本產品有兩種觸發路徑：

**路徑 A：長者主動發起（Reactive）**
```
長者說話 / 輸入文字
  → CareAgent 理解意圖
    → 普通問候 → 直接回應
    → 詢問症狀 → call get_vitals → 回報數值 + 建議
    → 詢問趨勢 → call_analysis_agent → AnalysisAgent 深度分析
```

**路徑 B：系統主動觸發（Proactive）**
```
IoT 感測器每 5 秒輪詢
  → APScheduler 背景執行
    → 正常 → 繼續輪詢
    → 異常（心率 > 120 或血氧 < 90%）
      → 觸發 CareAgent 主動對話（安撫 + 關心）
        → 數值持續異常 → call_alert_agent
          → AlertAgent 評估 → send_emergency_alert → 通報家屬
    → 定時觸發（早上 8 點）
      → CareAgent 主動問候 + 睡眠報告 + 用藥提醒
```

### 對話語氣設計（Vibe Design）

> 設計原則：像貼心晚輩，不像警報系統。

| 場景 | ❌ 錯誤語氣 | ✅ 正確語氣 |
|------|-----------|-----------|
| 異常偵測 | 「警告：您的心率異常，請立即就醫！」 | 「阿嬤，剛才量到你心跳快了一點，你現在有沒有覺得不舒服呀？」 |
| 用藥提醒 | 「用藥時間：08:00，請服用 Amlodipine。」 | 「阿嬤早安！早餐後記得把血壓藥吃了，昨晚睡得好不好？」 |
| 緊急通報後 | 「已通報聯絡人。」 | 「我已經告訴大文了，他知道你的情況。你先放輕鬆，我陪著你。」 |

### User Journey（核心場景：異常偵測流程）

```
[長者獨居，下午 3 點]
     │
     ▼
IoT 感測：心率 125 bpm，血氧 88%
     │
     ▼ (< 10 秒)
CareAgent 主動傳訊：
「阿嬤，我剛看到你的心跳有點快，你現在坐著還是站著？有沒有哪裡不舒服？」
     │
     ├─ 長者回：「我剛走路，有點喘」
     │    ▼
     │  CareAgent：「你先坐下來休息，我再量一次。」
     │  [30 秒後重新偵測 → 恢復正常 → 繼續關心]
     │
     └─ 長者無回應（5 分鐘）或數值持續惡化
          ▼
     call_alert_agent
          ▼
     AlertAgent 評估 → send_emergency_alert
          ▼
     「已通報陳大文（0912-345-678）：
      媽媽心率 125 bpm，血氧 88%，無法取得回應，請立即確認。」
          ▼
     家屬收到通知 → 致電 / 前往
```

---

## 6. Success Metrics

### Primary Metric
**異常事件覆蓋率**：IoT 偵測到閾值異常後，10 秒內觸發 Agent 主動對話的比例
- 目前（PoC）：APScheduler 5 秒輪詢，理論覆蓋率 > 99%（mock 環境）
- 目標（正式）：> 95%（含網路延遲、裝置斷線容錯）

### Secondary Metrics

| 指標 | 當前基線 | 目標 |
|------|---------|------|
| CareAgent 回應延遲 | 未量測（待補） | P50 < 2s，P90 < 3s |
| 用藥提醒觸達率 | 定時觸發（100% 觸發，長者確認未追蹤） | 長者確認點擊率 > 70% |
| 每日主動對話次數 | 1 次（早上問候） | 視異常頻率，平均 1–3 次/天 |
| AnalysisAgent 週趨勢摘要品質 | 主觀（無 eval） | 建立 eval 基準（Phase 2） |

### Guardrail Metrics（不能變差）

| 指標 | 說明 | 閾值 |
|------|------|------|
| 假警報率 | AlertAgent 觸發通報但數值正常 | < 5% |
| 用戶關閉主動功能率 | 長者或家屬關閉 proactive 功能 | < 10%（alert fatigue 訊號） |
| Token 成本/Session | 每次完整對話的 LLM 費用 | < USD 0.05 |

---

## 7. User Stories & Requirements

### Epic Hypothesis

> 「我們相信，對獨居長者提供 AI 主動關懷（而非被動等待求救），能夠在長者生理異常的 10 分鐘黃金窗口內介入，降低緊急事件的後果嚴重程度，同時讓家屬從被動焦慮轉為主動安心。我們將以異常事件覆蓋率和家屬滿意度作為衡量指標。」

---

### Story 1：生理異常主動觸發（核心功能）
**Proactive Trigger Story**

> 當 IoT 感測器偵測到生理數值超出閾值，系統在 10 秒內主動向長者發起關懷對話。

```
When: heart_rate > 120 bpm OR spo2 < 90%
Then: CareAgent initiates proactive conversation within 10 seconds

Acceptance Criteria:
- [ ] APScheduler 每 5 秒輪詢 get_vitals()
- [ ] 偵測異常後，pending_proactive 訊息在下一個 UI cycle 觸發
- [ ] CareAgent 的開場白包含：具體數值 + 溫暖語氣 + 開放式問題
- [ ] 單次 session 內，同一異常事件不重複觸發（避免轟炸）
- [ ] 觸發記錄寫入 log（timestamp, value, agent_response）
```

---

### Story 2：用藥主動提醒
**Scheduled Proactive Story**

> 在設定的用藥時間，Agent 主動發起提醒，並確認長者已知悉。

```
When: 定時排程到達（例如 08:00）
Then: CareAgent 主動發送用藥提醒

Acceptance Criteria:
- [ ] 提醒包含：藥名、時間、是否隨餐
- [ ] 語氣不是命令式，而是問候式（「記得吃藥了嗎？」）
- [ ] 同時附帶昨晚睡眠報告摘要（get_sleep_report）
- [ ] 若長者回應「已吃」，Agent 記錄並正向回饋
```

---

### Story 3：長者症狀描述 → 即時數據讀取
**Tool-Use Story**

> 當長者描述身體不適，Agent 主動讀取 IoT 即時數據並回應。

```
When: 長者說「頭暈」「不舒服」「胸悶」「喘」
Then: CareAgent 呼叫 get_vitals()，結合症狀給出生活建議

Acceptance Criteria:
- [ ] 包含「頭暈、不舒服、胸悶、喘、不對勁」等關鍵詞時，必定觸發 get_vitals
- [ ] 回應包含：即時心率 + 血氧 + 溫度 + 1 個具體建議
- [ ] 若數值異常：立即轉 Story 1 流程（Alert 路徑）
- [ ] 若數值正常：安撫 + 建議休息 + 跟進問候
- [ ] Tool call 到回應時間 < 3 秒
```

---

### Story 4：週健康趨勢分析
**Analysis Agent Story**

> 長者或家屬詢問近期健康狀況時，AnalysisAgent 提供深度趨勢摘要。

```
When: 長者詢問「最近健康如何」「我上週狀況好嗎」
Then: CareAgent 委派 call_analysis_agent，回傳趨勢摘要

Acceptance Criteria:
- [ ] AnalysisAgent 呼叫 get_health_trend(days=7)
- [ ] 輸出包含：心率趨勢（升 / 降 / 穩定）+ 血氧平均 + 睡眠質量
- [ ] 若有異常點（某天數值超閾值），明確標注日期
- [ ] 回應長度：3–5 句，不超過 100 字
- [ ] 整體 latency（含 AnalysisAgent 呼叫）< 8 秒
```

---

### Story 5：緊急通報流程
**Alert Story**

> 當生理數值持續異常或長者無回應，系統自動通報緊急聯絡人。

```
When: 心率 > 120 OR 血氧 < 90% 且長者 5 分鐘無回應
      OR CareAgent 判斷情況緊急
Then: AlertAgent 評估 → send_emergency_alert → 家屬通知

Acceptance Criteria:
- [ ] AlertAgent 先呼叫 get_vitals() 確認最新數值
- [ ] 若確認異常：呼叫 send_emergency_alert(reason)
- [ ] 通報內容包含：時間、具體數值、最後回應時間
- [ ] 通報後 CareAgent 繼續陪伴長者（「我已告訴大文了」）
- [ ] 一次異常事件只通報一次（去重邏輯）
- [ ] [PoC] send_emergency_alert 輸出 log；[Production] 真實發送 SMS / LINE
```

---

### Story 6：Memory — 對話連貫性
**Memory Story**

> Agent 在同一 session 內記住長者說過的事，不重複詢問。

```
When: 長者在對話中提到「我剛吃過飯了」
Then: 同一 session 內 Agent 不再問相關問題

Acceptance Criteria:
- [ ] Session memory 使用 InMemoryChatMessageHistory
- [ ] 同一 session（不重啟 Streamlit）內，之前對話內容可被引用
- [ ] Agent 回應中有明確引用先前資訊的表現（「你剛說剛吃完飯...」）
- [ ] Session 切換後（新啟動）記憶清空，不跨 session 污染
```

---

## 8. AI System Requirements

### 代理架構

```
主控：CareAgent（gpt-4o-mini）
  ├─ 負責：主對話、情緒理解、工具決策、子代理協調
  ├─ 工具：get_vitals / get_sleep_report / get_medication_schedule
  │          / call_analysis_agent / call_alert_agent
  └─ 記憶：_AgentWithMemory（session-scoped InMemoryChatMessageHistory）

子代理 1：AnalysisAgent（gemini-2.5-flash）
  ├─ 負責：7–30 天健康趨勢深度分析
  ├─ 工具：get_health_trend
  └─ 記憶：無（每次 stateless 呼叫）

子代理 2：AlertAgent（gpt-4o-mini）
  ├─ 負責：緊急數值評估 + 通報決策
  ├─ 工具：get_vitals / send_emergency_alert
  └─ 記憶：無（每次 stateless 呼叫）
```

**設計原則：最小權限**
- AlertAgent 無法直接對話，只能評估和通報
- AnalysisAgent 無法通報，只能分析
- send_emergency_alert 只有 AlertAgent 持有

---

### 工具 / Function Calling 規格

| 工具 | 持有者 | 觸發條件 | 輸入 | 輸出 |
|------|--------|---------|------|------|
| `get_vitals` | CareAgent, AlertAgent | 症狀關鍵詞 / 系統觸發 | — | `{heart_rate, spo2, temperature, timestamp}` |
| `get_sleep_report` | CareAgent | 早晨問候 / 詢問睡眠 | — | `{total_hours, deep_sleep_hours, wake_count, date}` |
| `get_medication_schedule` | CareAgent | 詢問用藥 / 提醒時間到 | — | `{name, medications[]}` |
| `get_health_trend` | AnalysisAgent | 趨勢分析請求 | `days: int` | `{avg_heart_rate, avg_spo2, avg_sleep, daily_records[]}` |
| `send_emergency_alert` | AlertAgent | 閾值超標確認 | `reason: str` | 通報確認字串 |
| `call_analysis_agent` | CareAgent | 趨勢問題偵測 | `query: str` | AnalysisAgent 輸出 |
| `call_alert_agent` | CareAgent | 異常數值偵測 | `situation: str` | AlertAgent 輸出 |

---

### Memory & Context 策略

| 層級 | 當前實作（PoC） | 生產目標 |
|------|--------------|---------|
| Session 記憶 | `InMemoryChatMessageHistory`（記憶體，重啟清空） | Redis / DynamoDB 持久化 |
| 長期健康歷史 | `health_history.json`（靜態假資料） | DynamoDB（真實感測器寫入） |
| Context 注入 | `health_profile.json` 動態讀入 system prompt | 啟動時從 DB 讀取，每日更新 |
| 跨 session | 未支援 | User ID 關聯，下次對話回憶上次狀況 |

---

### 效能需求

| 指標 | PoC 目標 | 生產目標 |
|------|---------|---------|
| CareAgent 回應延遲 | < 5s（開發環境） | P50 < 2s，P90 < 3s |
| Proactive 觸發延遲 | < 10s（APScheduler 5s + 處理） | < 10s（IoT Core rule 事件驅動） |
| AnalysisAgent 延遲 | < 10s（含 LLM 呼叫） | < 8s P90 |
| Token 成本/Session | 未追蹤（待補） | < USD 0.05 |
| 系統可用性 | N/A（本機） | > 99.5% |

---

### 評估策略（Eval）

**PoC 階段（當前）：**
- 手動測試：三個 Demo 場景（早晨問候 / 異常通報 / 用藥提醒）
- 測試覆蓋：34 個 pytest 測試（unit + integration mock）

**生產前需建立：**
- 工具呼叫準確性測試（Tool trigger rate for known inputs）
- 語氣合規測試（不出現醫療診斷語句）
- 假警報率基準（threshold 設定 calibration）
- Latency benchmark（P50 / P90 / P99）

---

### AI 特定風險

| 風險 | 說明 | 緩解措施 |
|------|------|---------|
| 醫療幻覺 | AI 給出診斷性建議（「你可能是心臟病」） | System prompt 明確禁止診斷語句；eval 定期掃描 |
| 警報疲勞 | 假警報過多 → 長者/家屬忽略通知 | 同一事件去重；rate limiting；閾值 calibration |
| 依賴風險 | 長者過度依賴 AI 判斷，延誤就醫 | 始終建議「有疑問請聯繫醫生或家人」 |
| 模型漂移 | LLM 更新後語氣或工具觸發改變 | 版本鎖定；更新後跑 regression test |

---

## 9. Technical Specifications

### PoC 架構（當前已實作）

```
[Mock IoT 感測器 data/mock_sensors.py]
  ↕ Python function call（同進程）
[APScheduler — 每 5 秒輪詢]
  → 偵測閾值超標
    → st.session_state.pending_proactive
      → st.rerun()
        → [Streamlit UI — app.py]
          → invoke_agent()
            → [CareAgent — agent/health_agent.py | gpt-4o-mini]
              ├─ Tools: get_vitals / get_sleep_report / get_medication_schedule
              ├─ [call_analysis_agent] → AnalysisAgent (gemini-2.5-flash)
              │     └─ Tools: get_health_trend
              └─ [call_alert_agent] → AlertAgent (gpt-4o-mini)
                    └─ Tools: get_vitals / send_emergency_alert (→ print log)
```

---

### 生產架構（AWS 藍圖）

```
[IoT 穿戴裝置 / 感測器]
  ↓ BLE → 手機 App → MQTT over TLS
[AWS IoT Core]
  ↓ IoT Rule（心率 > 120 OR 血氧 < 90%）
  ├─ → [AWS Lambda: anomaly-detector]
  │      → 寫入 DynamoDB（health_events 表）
  │      → 觸發 EventBridge → [Lambda: proactive-trigger]
  │            → 呼叫 LangChain Agent API
  │
  └─ [AWS Lambda: data-ingester]（5s 定時寫入）
       → DynamoDB（health_history 表）

[DynamoDB]
  ├─ Table: health_events（userId, timestamp, vitals, alert_sent）
  ├─ Table: health_history（userId, date, daily_avg）
  └─ Table: user_profiles（userId, name, conditions, medications, contacts）

[LangChain Agent Backend — ECS Fargate / Lambda]
  ├─ CareAgent（GPT-4o-mini via OpenAI API）
  ├─ AnalysisAgent（Gemini 2.5 Flash or AWS Bedrock Claude）
  └─ AlertAgent（GPT-4o-mini）
       └─ send_emergency_alert → AWS SNS → SMS / LINE Notify

[Client Layer]
  ├─ 長者端：語音 / 簡單 Chat UI（Mobile App）
  └─ 家屬端：Dashboard（健康摘要 + 警報歷史）
```

**AWS 服務對應說明：**

| AWS 服務 | 角色 | 對應 PoC 元件 |
|---------|------|-------------|
| IoT Core | 裝置連線 + MQTT 接收 | mock_sensors.py |
| Lambda (anomaly-detector) | 閾值判斷 + 事件觸發 | APScheduler `_proactive_monitor` |
| DynamoDB | 生理歷史 + 用戶資料 | health_history.json + health_profile.json |
| ECS Fargate | LangChain Agent 運行環境 | 本機 Streamlit |
| SNS | 緊急通報 SMS | send_emergency_alert print log |
| EventBridge | 定時觸發（用藥提醒） | APScheduler 定時 job |
| Bedrock（選用） | 替換 OpenAI，全 AWS 生態 | llm_factory.py（可擴充） |

---

### IoT Data Flow（詳細）

```
感測器讀值（每 5 秒）：
  heart_rate (bpm) | spo2 (%) | blood_pressure (mmHg) | steps (count) | temperature (°C)
    ↓
MQTT Publish → topic: homewellness/{userId}/vitals
    ↓
IoT Core Rule → SQL: SELECT * FROM 'homewellness/+/vitals'
    ↓
Lambda data-ingester → DynamoDB.put_item(health_events)
    ↓
Lambda anomaly-detector（if heart_rate > 120 OR spo2 < 90%）
    ↓
EventBridge event → Lambda proactive-trigger
    ↓
POST /agent/invoke { userId, trigger: "anomaly", vitals: {...} }
    ↓
CareAgent → proactive conversation
```

---

### 資料 Schema（DynamoDB）

```json
// health_events
{
  "userId": "user-001",
  "timestamp": "2026-05-26T15:30:00Z",
  "heart_rate": 125,
  "spo2": 88,
  "blood_pressure": { "systolic": 158, "diastolic": 95 },
  "steps_today": 342,
  "temperature": 26.5,
  "anomaly_detected": true,
  "alert_sent": true,
  "alert_contact": "0912-345-678"
}
```

---

### 安全與隱私

| 面向 | 設計 |
|------|------|
| 數據傳輸 | TLS 1.3（MQTT over TLS）；HTTPS API |
| 數據儲存 | DynamoDB 加密靜態資料（AES-256） |
| PHI 處理 | 健康數據不傳送至 LLM（只傳統計值和閾值判斷結果） |
| 同意模型 | 首次使用需長者 + 家屬雙方確認 |
| 警報資料保留 | 90 天後自動刪除（GDPR / 個資法考量） |
| 裝置認證 | IoT Core X.509 憑證 |

---

### 限制與假設（PoC 階段）

- 生理數據為 Mock（隨機生成），非真實感測器
- `send_emergency_alert` 只輸出 console log（未真實發送通知）
- Session 記憶存在記憶體中，重啟 Streamlit 後清空
- 單一用戶（陳阿嬤），未實作多用戶系統
- Latency 未量測（本機環境，無法代表生產延遲）
- 未實作血壓（blood_pressure）和步數（steps）感測器（已列入 Phase 2）

---

## 10. Out of Scope & Dependencies

### 本次 PoC 不包含

| 功能 | 排除原因 | 未來規劃 |
|------|---------|---------|
| 真實 IoT 硬體整合 | 需要硬體採購；PoC 驗證軟體架構為先 | Phase 2 |
| 血壓 / 步數感測器 | Mock 層缺失；作業週期不夠 | 補強項（見附錄） |
| 真實 SMS / LINE 通報 | 需 API 申請；PoC 用 log 代替 | Phase 2 |
| 多用戶 / 多長者管理 | 架構尚未設計 multi-tenancy | Phase 3 |
| 家屬 Dashboard | 超出 PoC 範圍 | Phase 3 |
| HIPAA / 個資法合規認證 | 需法律審查；PoC 無真實數據 | 商業化前 |
| 語音介面 | Streamlit 不支援；需 STT/TTS 整合 | Phase 2 |
| AWS 真實部署 | 架構在 PRD 定義，PoC 用本機模擬 | Phase 2 |
| Langflow 視覺化工作流 | 當前使用 LangChain Python；等價替代 | 可選加分項 |

### 依賴項目

| 依賴 | 類型 | 狀態 |
|------|------|------|
| OpenAI API Key | 外部 API | ✅ 需要 `.env` 設定 |
| Google Gemini API Key | 外部 API | ✅ 需要 `.env` 設定 |
| LangChain 1.x | 框架 | ✅ `requirements.txt` |
| Streamlit | UI 框架 | ✅ `requirements.txt` |
| APScheduler | 排程 | ✅ `requirements.txt` |

### Open Questions

1. **生產 LLM 選擇：** OpenAI vs. AWS Bedrock（Claude）vs. 自托管？
   - 考量：成本、數據隱私、延遲
2. **警報閾值個人化：** 統一閾值 vs. 依個人基線動態調整？
3. **長者互動模式：** 純文字 vs. 加入語音（STT/TTS）？
4. **隱私同意流程：** 長者認知能力不同，如何確保真實知情同意？

---

## 附錄：PoC 補強清單

> 這些項目在作業交付前建議補充，對應面試評分標準。

| 優先級 | 項目 | 對應評分 |
|--------|------|---------|
| P0 | 加入血壓、步數到 mock_sensors + tools | 產品完整性 |
| P0 | send_emergency_alert 改為真實通知（LINE Notify） | Vibe Coding 30% |
| P1 | app.py 加 Latency 計時 + Token 計數顯示 | 技術架構 40% |
| P1 | Streamlit 加 30 天趨勢折線圖 | 產品展示 |
| P2 | README 加架構圖 + Demo GIF | 整體印象 |
| P2 | llm_factory.py 加 Claude 模型支援 | 技術廣度 |
