# Version Control — HomeWellness Companion

## Commit Message 格式

`type(scope): 繁體中文描述`

| type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `refactor` | 重構（不影響行為） |
| `test` | 補測試 |
| `docs` | 更新文件 |
| `chore` | 依賴升級、設定更新 |

**scope 範例**：`agent`、`tools`、`prompts`、`memory`、`ui`、`data`、`tests`

**範例**：
```
feat(agent): 新增 AnalysisAgent 深度健康分析子代理
fix(memory): 修正 _AgentWithMemory 未清除舊 session 問題
test(tools): 補齊 get_health_trend days < 1 邊界測試
refactor(prompts): 抽取 _load_profile() 共用函式
chore(deps): 升級 langchain 至 1.3.1
```

---

## 禁止事項

- **禁止**在 commit message 加入 `Co-Authored-By: Claude` 或任何 AI 署名
- **禁止** commit `.env`（已加入 `.gitignore`）——只 commit `.env.example`
- **禁止** `--no-verify` 跳過 hook

---

## 環境變數安全

```bash
# .gitignore 已包含
.env

# 只 commit 這個
.env.example   # 內容：OPENAI_API_KEY=sk-your-key / ANTHROPIC_API_KEY=sk-ant-your-key
```

---

## 推送前確認

```bash
pytest tests/ -v       # 31 tests 全 pass
ruff check .           # 無 lint error
git status             # 確認沒有意外 staged 的檔案（特別是 .env）
```
