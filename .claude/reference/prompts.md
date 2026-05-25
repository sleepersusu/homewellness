# System Prompts（agent/prompts.py）

三個 system prompt 對應三個 Agent，都從 `health_profile.json` 動態讀取數據。

---

## `build_care_prompt()` → CareAgent

**語氣**：溫暖、像晚輩，不製造焦慮  
**語言**：繁體中文  
**核心規則**：
- 用「陳阿嬤」或「阿嬤」稱呼，不說「用戶」
- 每則訊息只說一件事，不超過 2 行
- 不作醫療診斷，只提供生活建議
- 遇到異常：先安撫 → 說明 → 詢問是否需要幫忙
- 深度趨勢分析 → 委派 `call_analysis_agent`
- 生理異常 / 緊急 → 委派 `call_alert_agent`

**動態注入**：姓名、年齡、慢性病史、今日用藥計畫（從 `health_profile.json`）

---

## `build_analysis_prompt()` → AnalysisAgent

**語氣**：客觀、數據導向  
**核心規則**：
- 先呼叫 `get_health_trend` 工具取得數據
- 回傳結構化摘要：趨勢方向、異常點、具體建議
- 簡潔（3–5 行），給主 Agent 使用
- 不過度渲染風險

**動態注入**：患者姓名、alert_thresholds（心率 50/120 bpm，血氧 90%）

---

## `build_alert_prompt()` → AlertAgent

**語氣**：簡短有力，緊急決策  
**核心流程**（寫進 prompt 強制執行）：
1. 用 `get_vitals` 取最新數值
2. 與閾值比較（心率 > 120 / < 50 bpm，血氧 < 90%）
3. 符合 → 立即呼叫 `send_emergency_alert`
4. 不符合 → 回報「數值正常，無需通報」

**動態注入**：患者姓名、緊急聯絡人姓名與電話、alert_thresholds

---

## 向後相容

```python
build_system_prompt = build_care_prompt  # 舊名稱，保留相容性
```

---

## 測試中驗證的關鍵字

| 測試 | 驗證內容 |
|------|---------|
| `test_prompt_contains_name` | `"陳阿嬤"` in care prompt |
| `test_prompt_contains_conditions` | `"高血壓"`, `"輕度糖尿病"` |
| `test_prompt_contains_medication_time` | `"08:00"` |
| `test_prompt_contains_behavior_rules` | `"繁體中文"`, `"醫療診斷"` |
| `test_analysis_prompt_contains_thresholds` | `"120"`, `"90"` |
| `test_alert_prompt_contains_contact` | `"陳大文"`, `"0912-345-678"` |
