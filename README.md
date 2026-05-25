# HomeWellness Companion — AI 健康伴侶 PoC

銀髮族主動式健康關懷 AI Agent，Technical PM (AI & IoT) 面試取回作業原型。

## 快速啟動

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定 API Key
cp .env.example .env
# 編輯 .env，填入 OPENAI_API_KEY 和 ANTHROPIC_API_KEY

# 3. 啟動
streamlit run app.py
```

## Live Demo 腳本（3 分鐘）

| 步驟 | 操作 | 展示重點 |
|------|------|---------|
| 1 | 點擊「🌅 模擬早晨問候」 | 主動觸發 + 長期記憶（姓名、病史） |
| 2 | 輸入「我今天頭有點暈」 | Tool Calling → get_vitals() |
| 3 | 點擊「🚨 模擬心率異常」 | 閾值觸發 → AlertAgent → send_emergency_alert() |
| 4 | 輸入「這週健康狀況怎麼樣？」 | CareAgent 委派 → AnalysisAgent → get_health_trend(7) |

## 技術架構

### Multi-Agent 設計

```
CareAgent（首腦 · gpt-4o-mini）
    ├─ 直接工具：get_vitals / get_sleep_report / get_medication_schedule
    ├─ → AnalysisAgent（claude-sonnet-4-6）：深度健康趨勢分析
    └─ → AlertAgent（gpt-4o-mini）：緊急數值評估與家屬通報
```

- **CareAgent**：主對話、工具決策、子代理協調（`health_agent.py`）
- **AnalysisAgent**：健康趨勢深度分析，使用更聰明的 Claude 模型（`analysis_agent.py`）
- **AlertAgent**：緊急應變，低延遲快速決策（`alert_agent.py`）
- **Memory**：`_AgentWithMemory` + `InMemoryChatMessageHistory`（CareAgent 的 session 記憶）
- **主動觸發**：APScheduler 背景心跳（每 5 秒輪詢感測數據）
- **UI**：Streamlit 左右分欄（數據面板 + 對話視窗）

## 專案結構

```
homewellness/
├── app.py                    # Streamlit 主程式 + APScheduler
├── agent/
│   ├── health_agent.py       # CareAgent（主控 orchestrator · gpt-4o-mini）
│   ├── analysis_agent.py     # AnalysisAgent（趨勢分析 · claude-sonnet-4-6）
│   ├── alert_agent.py        # AlertAgent（緊急通報 · gpt-4o-mini）
│   ├── tools.py              # 5 個 @tool 工具定義
│   ├── memory.py             # _AgentWithMemory session 記憶
│   └── prompts.py            # 三個 Agent 的 system prompt
├── data/
│   ├── mock_sensors.py       # 模擬即時 IoT 數據
│   ├── health_profile.json   # 長者健康檔案（用藥、病史、警報閾值）
│   └── health_history.json   # 近 30 天生理數據記錄
├── docs/
│   └── architecture.html     # 系統架構視覺化圖
├── tests/                    # pytest 測試套件（31 tests）
├── .env.example              # 環境變數範本
└── requirements.txt
```

## 環境變數

```env
OPENAI_API_KEY=sk-...         # CareAgent + AlertAgent（gpt-4o-mini）
ANTHROPIC_API_KEY=sk-ant-...  # AnalysisAgent（claude-sonnet-4-6）
```

## AWS 正式架構（簡報說明）

```
IoT 手環 → AWS IoT Core → Lambda → DynamoDB → API Gateway → Agent Service → SNS
```

## 執行測試

```bash
pytest tests/ -v
pytest tests/ --cov=agent --cov=data --cov-report=term-missing
```
