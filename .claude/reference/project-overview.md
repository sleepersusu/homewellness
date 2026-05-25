# HomeWellness Companion — 專案總覽

## 這是什麼

一個針對獨居長者的 **主動式 AI 健康伴侶**。主動監測 IoT 生理數據（mock），偵測異常自動觸發；同時提供自然語言對話，讓長者可以詢問健康狀況。

面試作業（Technical PM, AI & IoT role）——展示 IoT + Multi-Agent + Proactive AI 完整整合能力。

---

## 目錄結構

```
D:\homewellness\
├── app.py                    # Streamlit UI + APScheduler 主程式
├── agent/
│   ├── health_agent.py       # CareAgent（主控，gpt-4o-mini）
│   ├── analysis_agent.py     # AnalysisAgent（分析，claude-sonnet-4-6）
│   ├── alert_agent.py        # AlertAgent（緊急，gpt-4o-mini）
│   ├── tools.py              # 5 個 @tool 函式
│   ├── prompts.py            # 3 個 system prompt 建構函式
│   └── memory.py             # _AgentWithMemory session 記憶
├── data/
│   ├── mock_sensors.py       # Mock IoT 感測器數據
│   ├── health_profile.json   # 病患靜態檔案（陳阿嬤）
│   └── health_history.json   # 近 30 天生理歷史紀錄
└── tests/                    # pytest 測試（31 tests）
```

---

## 技術棧

| 層級 | 技術 | 版本 |
|------|------|------|
| UI | Streamlit | 1.57+ |
| 排程 | APScheduler | 3.11+ |
| Agent 框架 | LangChain | 1.3.1 |
| 主控 Agent | OpenAI gpt-4o-mini | via langchain-openai |
| 分析 Agent | Anthropic claude-sonnet-4-6 | via langchain-anthropic |
| 緊急 Agent | OpenAI gpt-4o-mini | via langchain-openai |
| 測試 | pytest + pytest-asyncio | 9.0+ |

---

## 啟動方式

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數（複製範本後填入 API Key）
cp .env.example .env
# 編輯 .env：填入 OPENAI_API_KEY 和 ANTHROPIC_API_KEY

# 啟動
streamlit run app.py
```

---

## 環境變數（`.env`）

```env
OPENAI_API_KEY=sk-...         # CareAgent + AlertAgent
ANTHROPIC_API_KEY=sk-ant-...  # AnalysisAgent
```

`.env` 已加入 `.gitignore`，只 commit `.env.example`。

---

## 測試

```bash
pytest tests/ -v
pytest tests/ --cov=agent --cov=data --cov-report=term-missing
```

31 個測試，全部 pass。`asyncio_mode = auto`（pytest.ini）。

---

## 相關參考文件

- `.claude/reference/multi-agent.md` — 三代理架構詳解
- `.claude/reference/tools.md` — 5 個工具函式
- `.claude/reference/memory.md` — Session 記憶實作
- `.claude/reference/prompts.md` — 三個 system prompt
- `.claude/reference/iot-layer.md` — Mock 感測器層
- `.claude/reference/ui-scheduler.md` — Streamlit UI + APScheduler
