# HomeWellness Companion — PRD Snippet
## 主動式健康關懷與用藥提醒

**作者：** Technical PM Candidate｜**日期：** 2026-05-26  
**完整版：** [PRD-detail.md](PRD-detail.md)

---

## Executive Summary

> 我們正在為獨居長者打造一個**主動感知、溫暖開口**的 AI 健康伴侶。  
> 裝置每 5 秒讀取生理數據，異常時不等長者求助——AI Agent 主動發起對話、提醒用藥、必要時自動通報家屬。  
> 目標：把緊急事件的發現時間從「數小時」壓縮到 **10 秒以內**。

---

## 1. User Journey — IoT 異常觸發主動對話

```
IoT 感測器（心率、血氧、血壓）
  ↓ 每 5 秒輪詢
閾值判斷
  ├─ 正常 → 繼續輪詢
  └─ 異常（心率 > 120、血氧 < 90%、或收縮壓 > 140 mmHg）
       ↓ < 10 秒
     CareAgent 主動開口
     「阿嬤，我看到你心跳有點快，你現在坐著嗎？有沒有不舒服？」
       ├─ 長者回應 → 安撫 + 建議 + 持續關注
       └─ 無回應（5 分鐘）或數值持續惡化
            ↓
          AlertAgent 評估 → 通報家屬
          「陳大文：媽媽心率 125 bpm，血氧 88%，
           5 分鐘無回應，請立即確認。」
```

**定時觸發（早上 08:00）：**
```
APScheduler 排程
  ↓
CareAgent 主動問候
「阿嬤早安！昨晚睡了 6.5 小時，早餐後記得吃血壓藥喔，今天感覺怎麼樣？」
```

---

## 2. Vibe Design — 讓長者感到溫暖與信任

| 場景 | ❌ 錯誤（警報系統） | ✅ 正確（貼心晚輩） |
|------|-----------------|-----------------|
| 異常偵測 | 「警告：心率異常，請立即就醫！」 | 「阿嬤，心跳快了一點，你現在有沒有哪裡不舒服呀？」 |
| 用藥提醒 | 「08:00 服藥時間：Amlodipine。」 | 「早安！早餐後記得把血壓藥吃了，昨晚睡得好不好？」 |
| 緊急通報後 | 「已通報聯絡人。」 | 「我已經告訴大文了，他知道你的情況，你先放輕鬆，我陪著你。」 |
| 長者說頭暈 | 「正在讀取血壓數據。」 | 「頭有點暈嗎？我幫你量一下血壓，你先坐著別動。」→ 呼叫 `get_vitals` |

**設計原則：** 每則訊息只說一件事 · 句子不超過 2 行 · 用名字不用「用戶」· 不作醫療診斷

---

## 3. 核心 User Stories

### Story 1：生理異常主動觸發
**As** 獨居長者，**I want** 當我心率或血氧異常時 AI 主動關心我，  
**So that** 我不需要自己判斷是否嚴重，也不會在危險時獨自面對。

```
Acceptance Criteria:
- [ ] 心率 > 120 bpm 或血氧 < 90%，10 秒內 CareAgent 主動發訊
- [ ] 開場白包含具體數值 + 溫暖語氣 + 開放式問題
- [ ] 同一事件不重複觸發（防轟炸）
- [ ] 5 分鐘無回應 → 自動轉 AlertAgent
```

### Story 2：症狀描述 → 即時血壓 / 生理讀取
**As** 長者，**I want** 說「我頭有點暈」時 AI 自動讀取我的生理數據，  
**So that** 我不需要自己操作裝置，AI 幫我判斷是否需要關注。

```
Acceptance Criteria:
- [ ] 「頭暈、不舒服、胸悶、喘」等關鍵詞必定觸發 get_vitals
- [ ] 回應包含：血壓 + 心率 + 血氧 + 1 個具體建議
- [ ] Tool call 到回應時間 < 3 秒
- [ ] 數值異常時升級至 AlertAgent 流程
```

### Story 3：用藥主動提醒
**As** 有慢性病的長者，**I want** 在用藥時間 AI 主動提醒我，  
**So that** 我不會忘記吃藥，也感覺有人在陪伴和照顧我。

```
Acceptance Criteria:
- [ ] 定時在設定時間主動發送提醒（APScheduler）
- [ ] 提醒包含藥名 + 是否隨餐 + 昨晚睡眠摘要
- [ ] 語氣為問候式（非命令式）
- [ ] Agent 記住「已吃藥」的回應，不重複提醒
```

---

## 4. Success Metrics

| 類型 | 指標 | 目標 |
|------|------|------|
| **Primary** | 異常事件 10 秒內觸發率 | > 95% |
| Secondary | CareAgent 回應延遲 P90 | < 3s |
| Secondary | 用藥提醒確認率 | > 70% |
| Guardrail | 假警報率（AlertAgent 誤觸發） | < 5% |
| Guardrail | Token 成本 / Session | < USD 0.05 |

---

## 5. AI 工作流設計

```
用戶輸入 / 系統觸發
  ↓
CareAgent（gpt-4o-mini）— 主控 Orchestrator
  ├─ 工具：get_vitals / get_sleep_report / get_medication_schedule
  │         → 直接回應長者
  │
  ├─ 偵測趨勢問題 → call_analysis_agent
  │    └─ AnalysisAgent（gemini-2.5-flash）
  │         └─ 工具：get_health_trend(days=N)
  │         → 回傳趨勢摘要給 CareAgent
  │
  └─ 偵測數值異常 → call_alert_agent
       └─ AlertAgent（gpt-4o-mini）
            ├─ 工具：get_vitals（確認最新數值）
            └─ 工具：send_emergency_alert(reason)
                 → 通報家屬
```

**Memory 策略：**  
- Session 記憶：`_AgentWithMemory` + `InMemoryChatMessageHistory`（對話中不重複詢問）  
- 長期健康歷史：`health_history.json` → 生產環境改為 DynamoDB

**Proactive Trigger 機制：**  
```python
APScheduler（interval=5s）
  → get_mock_vitals() 讀取數值
  → 超閾值 → st.session_state.pending_proactive = "（系統觸發）異常訊息"
  → st.rerun() → invoke_agent()
```

---

## 6. AWS 系統架構圖

```
┌─────────────────────────────────────────────────────────┐
│                    IoT 裝置層                            │
│  [穿戴感測器] → BLE → [手機 App] → MQTT/TLS            │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  AWS 雲端層                              │
│                                                         │
│  [AWS IoT Core] ──Rule──→ [Lambda: anomaly-detector]   │
│       │                        │                        │
│       ↓                        ↓                        │
│  [Lambda: data-ingester]  [EventBridge]                 │
│       │                        │                        │
│       ↓                        ↓                        │
│  [DynamoDB: health_events] [Lambda: proactive-trigger]  │
│  [DynamoDB: health_history]     │                       │
│  [DynamoDB: user_profiles]      ↓                       │
│                          POST /agent/invoke              │
└─────────────────────────────────┬───────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────┐
│                  AI Agent 層（ECS Fargate）              │
│                                                         │
│  CareAgent (gpt-4o-mini)                               │
│    ├─ AnalysisAgent (Gemini / Bedrock)                 │
│    └─ AlertAgent → [AWS SNS] → SMS / LINE Notify       │
└─────────────────────────────────┬───────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────┐
│                  Client 層                              │
│  長者端：語音 Chat UI（Mobile App）                     │
│  家屬端：健康摘要 Dashboard                             │
└─────────────────────────────────────────────────────────┘

PoC 對應：
  IoT Core     → mock_sensors.py + APScheduler
  DynamoDB     → health_history.json / health_profile.json
  ECS Fargate  → streamlit run app.py（本機）
  SNS          → send_emergency_alert()（目前為 log 輸出）
```

---

*完整版（市場分析、全部 User Story、詳細 Schema、實作計畫）→ [PRD-detail.md](PRD-detail.md)*
