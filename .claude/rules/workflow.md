# Workflow Guidelines — HomeWellness Companion

## 開發流程

```
需求確認
  → 影響分析（列出受影響的 agent / tool / prompt / test）
    → TDD：先寫測試 → 確認 fail → 實作 → 確認 pass
      → 品質審查（型別標注、docstring、命名規範）
        → git commit
```

---

## 修改各層的注意事項

### 修改 `agent/tools.py`

1. 先在 `tests/test_tools.py` 寫測試（mock `data.mock_sensors`）
2. 更新 tool docstring——LLM 靠 docstring 決定何時呼叫
3. 確認哪些 Agent 需要這個工具，更新對應的 `build_*_agent()`

### 修改 `agent/prompts.py`

1. 在 `tests/test_prompts.py` 新增關鍵字驗證測試
2. 從 `health_profile.json` 動態讀取，不硬寫病患資料

### 新增 / 修改 Agent

1. 子代理（非 CareAgent）不加記憶 wrapper
2. lazy import 放在 `build_agent()` 函式體內（見 `health_agent.py`）
3. 新 Agent 對應新的 `build_*_agent()` + `invoke_*_agent()` 函式

### 修改 `data/health_profile.json`

影響所有 prompt 和 tool——修改後全跑一次 `pytest tests/test_prompts.py`。

### 修改 `app.py`

Streamlit UI 無法純靠 pytest 驗證，需啟動 `streamlit run app.py` 手動測試：
- 三個 Demo 按鈕均可觸發
- APScheduler 心跳正常（模擬異常後 5 秒內自動出現 Agent 訊息）
- 對話歷史正確顯示

---

## 常用指令

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動 app
streamlit run app.py

# 測試
pytest tests/ -v
pytest tests/ --cov=agent --cov=data --cov-report=term-missing

# Linting
ruff check .
ruff format .
```

---

## Git Commit 規範

格式：`type(scope): 繁體中文描述`

| type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `refactor` | 重構（不影響行為） |
| `test` | 補測試 |
| `docs` | 更新文件 |
| `chore` | 依賴、設定更新 |

範例：
```
feat(agent): 新增多代理協調架構
fix(memory): 修正 session_id 預設值未隔離問題
test(tools): 補齊 send_emergency_alert 測試
refactor(prompts): 統一三個 prompt 的閾值讀取邏輯
```

**禁止**：`Co-Authored-By: Claude` 或任何 AI 署名
