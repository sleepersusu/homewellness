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

- **AI Agent**：LangChain 1.x `create_agent` + Claude claude-sonnet-4-6
- **Memory**：`_AgentWithMemory` + `InMemoryChatMessageHistory`（短期對話記憶）
- **Tools**：5 個工具（vitals / medication / sleep / trend / alert）
- **主動觸發**：APScheduler 背景心跳（每 5 秒輪詢感測數據）
- **UI**：Streamlit 左右分欄（數據面板 + 對話視窗）
- **工作流圖**：`langflow/workflow.json`（Langflow 視覺化導出）

## 專案結構

```
homewellness/
├── app.py                   # Streamlit 主程式（UI 入口）
├── agent/
│   ├── health_agent.py      # LangChain agent 組裝
│   ├── tools.py             # 5 個 @tool 工具定義
│   ├── memory.py            # 短期記憶管理
│   └── prompts.py           # System prompt（語氣設計）
├── data/
│   ├── mock_sensors.py      # 模擬即時 IoT 數據
│   ├── health_profile.json  # 長者健康檔案（用藥、病史）
│   └── health_history.json  # 近 30 天生理數據記錄
├── langflow/
│   └── workflow.json        # Langflow 視覺化工作流導出
├── tests/                   # pytest 測試套件（25 tests）
├── .env.example             # 環境變數範本
└── requirements.txt
```

## AWS 正式架構（簡報說明）

```
IoT 手環 → AWS IoT Core → Lambda → DynamoDB → API Gateway → Agent Service → SNS
```

## 執行測試

```bash
pytest -v --cov=agent --cov=data --cov-report=term-missing
```
