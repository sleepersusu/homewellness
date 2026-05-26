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
│   ├── health_agent.py       # CareAgent（主控，預設 gpt-4o-mini）
│   ├── analysis_agent.py     # AnalysisAgent（分析，預設 gemini-2.5-flash）
│   ├── alert_agent.py        # AlertAgent（緊急，預設 gpt-4o-mini）
│   ├── llm_factory.py        # LLM 工廠：get_llm(model_name) → OpenAI / Gemini
│   ├── tools.py              # 5 個 @tool 函式
│   ├── prompts.py            # 3 個 system prompt 建構函式
│   └── memory.py             # _AgentWithMemory session 記憶
├── data/
│   ├── mock_sensors.py       # Mock IoT 感測器數據
│   ├── health_profile.json   # 病患靜態檔案（陳阿嬤）
│   └── health_history.json   # 近 30 天生理歷史紀錄
└── tests/                    # pytest 測試（47 tests）
```

---

## 技術棧

| 層級 | 技術 | 版本 |
|------|------|------|
| UI | Streamlit | 1.57+ |
| 排程 | APScheduler | 3.11+ |
| Agent 框架 | LangChain | 1.3.1 |
| OpenAI 模型 | gpt-4o-mini / gpt-4o | via langchain-openai |
| Gemini 模型 | gemini-2.5-flash / gemini-2.5-pro / gemini-2.0-flash | via langchain-google-genai |
| 模型切換 | Streamlit sidebar 即時選擇，無需重啟 | agent/llm_factory.py |
| 測試 | pytest + pytest-asyncio | 9.0+ |

---

## 啟動方式

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數（複製範本後填入 API Key）
cp .env.example .env
# 編輯 .env：填入 OPENAI_API_KEY 和 GOOGLE_API_KEY

# 啟動
streamlit run app.py
```

---

## 環境變數（`.env`）

```env
OPENAI_API_KEY=sk-...    # 使用 gpt-4o-mini / gpt-4o 時需要
GOOGLE_API_KEY=...       # 使用 gemini-* 時需要（Google AI Studio 申請）
```

`.env` 已加入 `.gitignore`，只 commit `.env.example`。

---

## 測試

```bash
pytest tests/ -v
pytest tests/ --cov=agent --cov=data --cov-report=term-missing
```

47 個測試，全部 pass。`asyncio_mode = auto`（pytest.ini）。

---

## 相關參考文件

- `.claude/reference/multi-agent.md` — 三代理架構詳解
- `.claude/reference/tools.md` — 5 個工具函式
- `.claude/reference/memory.md` — Session 記憶實作
- `.claude/reference/prompts.md` — 三個 system prompt
- `.claude/reference/iot-layer.md` — Mock 感測器層
- `.claude/reference/ui-scheduler.md` — Streamlit UI + APScheduler
