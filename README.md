# HomeWellness Companion

> A proactive AI health companion that senses first and speaks up warmly — built for seniors living alone, combining IoT sensing, multi-agent orchestration, and proactive triggers.

*[繁體中文版 README](README.zh-TW.md)*

---

## In One Sentence

`st.fragment(run_every=5s)` polls IoT vitals every 5 seconds. When it detects an anomaly (heart rate, SpO2, blood pressure), it automatically triggers CareAgent to start the conversation. Seniors can also type a symptom at any time — the AI reads live readings and responds immediately.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Fill in OPENAI_API_KEY and GOOGLE_API_KEY in .env

# 3. Run
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Live Demo Script (3 minutes)

| Step | Action | What it shows |
|------|--------|---------------|
| 1 | Click "🌅 Simulate Morning Greeting" | Proactive trigger + session memory (name, medical history, medication) |
| 2 | Type "I feel a bit dizzy today" | Tool calling → `get_vitals()` reads live blood pressure / heart rate / SpO2 |
| 3 | Switch scenario to "Tachycardia" → wait 5s | st.fragment threshold trigger → AlertAgent → `send_emergency_alert()` |
| 4 | Type "How has my health been this week?" | CareAgent delegates → AnalysisAgent → `get_health_trend(7)` |
| 5 | Switch scenario to "Hypertension" → wait 5s | Systolic > 140 mmHg triggers the proactive care flow |

---

## Features

| Feature | Description |
|---------|-------------|
| **Proactive trigger** | Heart rate > 120 bpm, SpO2 < 90%, systolic > 140 mmHg → CareAgent speaks up within 10 seconds |
| **Multi-agent orchestration** | CareAgent orchestrates and delegates to AnalysisAgent (trends) or AlertAgent (emergencies) as needed |
| **Live vitals monitoring** | Heart rate / SpO2 / blood pressure / step count / body temperature, with 5 simulated scenarios |
| **Session memory** | Never re-asks within a conversation; `_AgentWithMemory` keeps the context coherent |
| **Tone design** | Speaks like a caring grandchild, uses her name (Grandma), never diagnoses, one idea per message |
| **Switchable models** | Pick each agent's LLM (OpenAI / Gemini) live from the sidebar — no restart needed |
| **Performance monitoring** | Sidebar shows per-response latency, token usage, cost estimate, and cumulative stats |
| **Agent self-scheduling** | After an alert, AlertAgent calls `schedule_followup` to check back N minutes later (cron-as-tool) |
| **30-day trend dashboard** | Dedicated tab: heart rate / SpO2 / systolic line charts + alert threshold guides + day-over-day delta |

---

## System Architecture

```
IoT sensors (mock_sensors.py)
  └─ st.fragment polls every 5s (main thread, no threading issues)
       ├─ Normal   → keep polling
       └─ Abnormal → pending_proactive → st.rerun()
                    ↓
            CareAgent (gpt-4o-mini) — the orchestrator
              ├─ Tools: get_vitals / get_sleep_report / get_medication_schedule
              ├─ Trend questions → AnalysisAgent (gemini-2.5-flash) → get_health_trend(N)
              └─ Abnormal values → AlertAgent (gpt-4o-mini) → send_emergency_alert(reason)
                                  └─ schedule_followup(reason) → threading.Timer
                                       └─ re-enters pending_proactive N minutes later (follow-up check)
```

**Mapping to a production AWS architecture:**

| Production | PoC equivalent |
|------------|----------------|
| AWS IoT Core (MQTT/TLS) | `mock_sensors.py` |
| Lambda `anomaly-detector` | st.fragment threshold check |
| Lambda `data-ingester` | — |
| DynamoDB `health_events` | `health_history.json` |
| ECS Fargate (LangChain) | `streamlit run app.py` |
| AWS SNS | `send_emergency_alert()` (currently logs output) |

See `docs/PRD.md` §5 for the full architecture write-up (in Traditional Chinese).

---

## Project Structure

```
homewellness/
├── app.py                    # Streamlit UI + st.fragment heartbeat monitoring
├── charts.py                 # Plotly 30-day health trend charts (build_trend_chart)
├── agent/
│   ├── health_agent.py       # CareAgent (main orchestrator)
│   ├── analysis_agent.py     # AnalysisAgent (deep trend analysis)
│   ├── alert_agent.py        # AlertAgent (emergency assessment and notification)
│   ├── llm_factory.py        # LLM factory: unified OpenAI / Gemini interface
│   ├── tools.py              # 6 @tool functions (least-privilege allocation)
│   ├── prompts.py            # 3 build_*_prompt() functions, patient data injected dynamically
│   ├── memory.py             # _AgentWithMemory + InMemoryChatMessageHistory
│   └── scheduler_tools.py    # Follow-up queue + Timer self-scheduling (cron-as-tool)
├── data/
│   ├── mock_sensors.py       # Mock IoT (heart rate / SpO2 / blood pressure / steps / temperature)
│   ├── health_profile.json   # Static patient data (Grandma Chen) + alert thresholds
│   └── health_history.json   # Last 30 days of vitals history
├── docs/
│   ├── PRD.md                   # Product requirements (user journey / user stories / success metrics)
│   ├── HomeWellness_Proactive_AI (1).pdf  # Slide deck
│   └── superpowers/             # Design specs and implementation plans
├── tests/                    # 63 pytest tests
├── .env.example
└── requirements.txt
```

---

## Alert Thresholds

| Metric | Alert condition |
|--------|-----------------|
| Heart rate | < 50 bpm or > 120 bpm |
| SpO2 | < 90% |
| Systolic blood pressure | > 140 mmHg |

---

## Running Tests

```bash
# All tests (63)
pytest tests/ -v

# With coverage report
pytest tests/ --cov=agent --cov=data --cov-report=term-missing
```

---

## Environment Variables

```env
OPENAI_API_KEY=sk-...      # CareAgent + AlertAgent (gpt-4o-mini)
GOOGLE_API_KEY=...         # AnalysisAgent (gemini-2.5-flash)
```

Models can be switched live from the Streamlit sidebar — no restart required.

---

## Design Principles

- **Least privilege**: `send_emergency_alert` is granted only to AlertAgent; `get_health_trend` only to AnalysisAgent
- **Tone design**: one idea per message, use her name instead of "the user", never give a medical diagnosis
- **Lazy import**: AnalysisAgent / AlertAgent are imported inside the body of `build_agent()` to prevent circular imports
- **No** `RunnableWithMessageHistory` (deprecated) — replaced by the hand-rolled `_AgentWithMemory`
- **Cron-as-tool**: `schedule_followup` lets AlertAgent schedule its own follow-up without an external cron — the agent owns its timeline
