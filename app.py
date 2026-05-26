# app.py
import json
import streamlit as st
from datetime import time as dtime
from pathlib import Path
from dotenv import load_dotenv
from agent.health_agent import build_agent, invoke_agent
from agent.llm_factory import AVAILABLE_MODELS
from charts import build_trend_chart
from data.mock_sensors import (
    get_mock_vitals,
    get_mock_sleep_report,
    get_mock_health_history,
    set_simulate_abnormal,
    set_vitals_override,
)

load_dotenv()

_PROFILE = json.loads(Path("data/health_profile.json").read_text(encoding="utf-8"))

_SCENARIO_OPTIONS = ["正常", "心跳過快", "心跳過慢", "低血氧", "高血壓", "自訂"]
_SCENARIO_PRESETS: dict[str, dict] = {
    "心跳過快": {"heart_rate": 125, "spo2": 88},
    "心跳過慢": {"heart_rate": 42, "spo2": 96},
    "低血氧":   {"heart_rate": 95, "spo2": 85},
    "高血壓":   {"blood_pressure": {"systolic": 168, "diastolic": 108}},
}

st.set_page_config(
    page_title="HomeWellness Companion",
    page_icon="🏥",
    layout="wide",
)

# ── Sidebar：模型選擇 ──────────────────────────────────
with st.sidebar:
    st.header("⚙️ 模型設定")
    care_model = st.selectbox(
        "🤖 CareAgent（主對話）",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index("gpt-4o-mini"),
        key="care_model",
    )
    analysis_model = st.selectbox(
        "🧪 AnalysisAgent（趨勢分析）",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index("gemini-2.5-flash"),
        key="analysis_model",
    )
    alert_model = st.selectbox(
        "🚨 AlertAgent（緊急通報）",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index("gpt-4o-mini"),
        key="alert_model",
    )

    model_key = f"{care_model}|{analysis_model}|{alert_model}"
    if st.session_state.get("model_key") != model_key:
        st.session_state.model_key = model_key
        st.session_state.pop("agent", None)
        st.session_state.messages = []

    st.caption("變更模型後自動重建 Agent 並清除對話記錄")

    st.divider()
    st.header("📊 效能監控")

    last = st.session_state.get("last_stats")
    if last:
        st.subheader("最近一次")
        m1, m2 = st.columns(2)
        m1.metric("⏱️ 延遲", f"{last['latency']} s")
        m2.metric("💰 費用", f"${last['cost_usd']:.5f}")
        m3, m4 = st.columns(2)
        m3.metric("📥 輸入 Token", f"{last['input_tokens']:,}")
        m4.metric("📤 輸出 Token", f"{last['output_tokens']:,}")
        st.caption(f"模型：{last['model']}")
    else:
        st.caption("尚無對話紀錄")

    cum = st.session_state.get("cumulative_stats", {})
    if cum.get("calls", 0) > 0:
        st.subheader("累計統計")
        st.metric("🔢 對話次數", cum["calls"])
        st.metric("🪙 總 Token", f"{cum['total_tokens']:,}")
        st.metric("💵 總費用", f"${cum['total_cost']:.4f}")

    st.divider()
    st.header("⏰ 追蹤設定")
    from agent.scheduler_tools import set_default_followup_minutes
    followup_min = st.slider(
        "AlertAgent 通報後追蹤間隔",
        min_value=1, max_value=120, value=30, step=1,
        format="%d 分鐘",
        key="followup_minutes",
    )
    set_default_followup_minutes(followup_min)
    st.caption(f"通報後 {followup_min} 分鐘自動追蹤確認阿嬤狀況")

# ── Session State Init ────────────────────────────────
if "agent" not in st.session_state:
    with st.spinner(f"載入 AI 健康伴侶（{care_model} / {analysis_model} / {alert_model}）..."):
        st.session_state.agent = build_agent(
            care_model=care_model,
            analysis_model=analysis_model,
            alert_model=alert_model,
        )
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vitals_scenario" not in st.session_state:
    st.session_state.vitals_scenario = "正常"
if "med_overrides" not in st.session_state:
    st.session_state.med_overrides = {
        med["name"]: med["time"] for med in _PROFILE["medications"]
    }
if "pending_proactive" not in st.session_state:
    st.session_state.pending_proactive = None

# ── APScheduler Heartbeat ─────────────────────────────
from apscheduler.schedulers.background import BackgroundScheduler

if "scheduler_started" not in st.session_state:
    def _proactive_monitor():
        from agent.scheduler_tools import pop_followup
        followup = pop_followup()
        if followup:
            st.session_state["pending_proactive"] = followup
            return

        vitals = get_mock_vitals()
        thresholds = json.loads(
            Path("data/health_profile.json").read_text(encoding="utf-8")
        )["alert_thresholds"]
        bp = vitals["blood_pressure"]
        if (
            vitals["heart_rate"] > thresholds["heart_rate_high"]
            or vitals["spo2"] < thresholds["spo2_low"]
            or bp["systolic"] > thresholds["systolic_high"]
        ):
            st.session_state["pending_proactive"] = (
                f"（系統觸發）偵測到異常數值：心率 {vitals['heart_rate']} bpm，"
                f"血氧 {vitals['spo2']}%，"
                f"血壓 {bp['systolic']}/{bp['diastolic']} mmHg，請立即關心陳阿嬤。"
            )

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_proactive_monitor, "interval", seconds=5)
    _scheduler.start()
    st.session_state.scheduler_started = True

# ── Session State: Stats ──────────────────────────────
if "last_stats" not in st.session_state:
    st.session_state.last_stats = None
if "cumulative_stats" not in st.session_state:
    st.session_state.cumulative_stats = {"calls": 0, "total_tokens": 0, "total_cost": 0.0}


def _record_stats(stats: dict) -> None:
    st.session_state.last_stats = stats
    c = st.session_state.cumulative_stats
    c["calls"] += 1
    c["total_tokens"] += stats["total_tokens"]
    c["total_cost"] += stats["cost_usd"]


# ── Handle Proactive Trigger ──────────────────────────
if st.session_state.pending_proactive:
    _msg = st.session_state.pending_proactive
    st.session_state.pending_proactive = None
    with st.spinner("Agent 偵測到異常..."):
        _resp, _stats = invoke_agent(
            st.session_state.agent, _msg, model=st.session_state.get("care_model", "gpt-4o-mini")
        )
    _record_stats(_stats)
    st.session_state.messages.append({"role": "assistant", "content": _resp})
    st.rerun()

# ── Layout ────────────────────────────────────────────
st.title("🏥 HomeWellness Companion")
tab_live, tab_trend = st.tabs(["💬 即時監測與對話", "📈 健康趨勢儀表板"])
col_data, col_chat = tab_live.columns([1, 2])

# Left: Data Panel
with col_data:
    sleep = get_mock_sleep_report()

    # ── 即時生理數據 ──────────────────────────────────
    st.subheader("📊 即時生理數據")

    th = _PROFILE["alert_thresholds"]
    _c1, _c2, _c3 = st.columns(3)
    _c1.caption(f"💓 心率\n< {th['heart_rate_low']} 或 > {th['heart_rate_high']} bpm")
    _c2.caption(f"🩸 血氧\n< {th['spo2_low']}%")
    _c3.caption(f"🩺 收縮壓\n> {th['systolic_high']} mmHg")

    with st.expander("🎛️ 場景模擬", expanded=True):
        scenario = st.radio(
            "場景",
            _SCENARIO_OPTIONS,
            key="vitals_scenario",
            horizontal=True,
            label_visibility="collapsed",
        )
        if scenario in _SCENARIO_PRESETS:
            set_vitals_override(_SCENARIO_PRESETS[scenario])
        elif scenario == "自訂":
            c1, c2, c3 = st.columns(3)
            hr_val   = c1.slider("心率 bpm",   30, 200, 75,   key="custom_hr")
            spo2_val = c2.slider("血氧 %",      70, 100, 97,   key="custom_spo2")
            temp_val = c3.slider("溫度 °C",    15.0, 40.0, 26.0, step=0.1, key="custom_temp")
            c4, c5, _ = st.columns(3)
            systolic_val  = c4.slider("收縮壓 mmHg", 90, 200, 120, key="custom_systolic")
            diastolic_val = c5.slider("舒張壓 mmHg", 60, 130, 80,  key="custom_diastolic")
            set_vitals_override({
                "heart_rate": hr_val,
                "spo2": spo2_val,
                "temperature": temp_val,
                "blood_pressure": {"systolic": systolic_val, "diastolic": diastolic_val},
            })
        else:
            set_vitals_override(None)
            set_simulate_abnormal(False)

    vitals = get_mock_vitals()
    hr   = vitals["heart_rate"]
    spo2 = vitals["spo2"]
    bp   = vitals["blood_pressure"]
    st.metric("💓 心率",     f"{hr} bpm",
              "⚠️ 異常" if hr > th["heart_rate_high"] or hr < th["heart_rate_low"] else "正常")
    st.metric("🩸 血氧",     f"{spo2}%",
              "⚠️ 異常" if spo2 < th["spo2_low"] else "正常")
    st.metric("🩺 血壓",     f"{bp['systolic']}/{bp['diastolic']} mmHg",
              "⚠️ 異常" if bp["systolic"] > th["systolic_high"] else "正常")
    st.metric("🚶 今日步數", f"{vitals['steps']:,} 步")
    st.metric("😴 昨晚睡眠", f"{sleep['total_hours']} hrs")
    st.metric("🌡️ 環境溫度", f"{vitals['temperature']}°C")

    st.divider()

    # ── 今日用藥 ──────────────────────────────────────
    st.subheader("💊 今日用藥")
    for med in _PROFILE["medications"]:
        t = st.session_state.med_overrides.get(med["name"], med["time"])
        st.write(f"⏰ {t} — {med['name']}")

    with st.expander("✏️ 調整用藥時間"):
        for i, med in enumerate(_PROFILE["medications"]):
            current = st.session_state.med_overrides.get(med["name"], med["time"])
            h, m = map(int, current.split(":"))
            new_t = st.time_input(med["name"], value=dtime(h, m), key=f"med_time_{i}")
            st.session_state.med_overrides[med["name"]] = new_t.strftime("%H:%M")
        if st.button("重置為預設時間", use_container_width=True):
            for i in range(len(_PROFILE["medications"])):
                st.session_state.pop(f"med_time_{i}", None)
            st.session_state.med_overrides = {
                med["name"]: med["time"] for med in _PROFILE["medications"]
            }
            st.rerun()

    st.divider()

    # ── Demo 控制台 ────────────────────────────────────
    st.subheader("🎮 Demo 控制台")

    if st.button("🌅 模擬早晨問候", use_container_width=True):
        prompt = (
            "（系統觸發）現在是早上8點，請主動問候陳阿嬤，"
            "分享昨晚睡眠報告，並提醒早餐後服用降血壓藥。"
        )
        with st.spinner("Agent 思考中..."):
            response, stats = invoke_agent(
                st.session_state.agent, prompt,
                model=st.session_state.get("care_model", "gpt-4o-mini"),
            )
        _record_stats(stats)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🚨 模擬心率異常（125 bpm）", use_container_width=True):
        st.session_state.vitals_scenario = "心跳過快"
        set_vitals_override({"heart_rate": 125, "spo2": 88})
        prompt = (
            "（系統觸發）偵測到心率 125 bpm，血氧 88%，"
            "請立即關心陳阿嬤，並觸發緊急通報流程。"
        )
        with st.spinner("Agent 處理中..."):
            response, stats = invoke_agent(
                st.session_state.agent, prompt,
                model=st.session_state.get("care_model", "gpt-4o-mini"),
            )
        _record_stats(stats)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# Right: Chat
with col_chat:
    st.subheader("💬 健康對話")
    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if user_input := st.chat_input("和阿嬤的健康伴侶說話..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("思考中..."):
            response, stats = invoke_agent(
                st.session_state.agent, user_input,
                model=st.session_state.get("care_model", "gpt-4o-mini"),
            )
        _record_stats(stats)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ── 趨勢儀表板 ────────────────────────────────────────
with tab_trend:
    history = get_mock_health_history(30)
    yesterday = history[-1]  # 最新一筆（昨日均值）

    st.subheader("📊 當前數值 vs 昨日均值")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric(
        "💓 心率",
        f"{vitals['heart_rate']} bpm",
        delta=f"{vitals['heart_rate'] - round(yesterday['heart_rate_avg'])} bpm",
    )
    d2.metric(
        "🩸 血氧",
        f"{vitals['spo2']}%",
        delta=f"{vitals['spo2'] - round(yesterday['spo2_avg'])}%",
    )
    d3.metric(
        "🩺 收縮壓",
        f"{vitals['blood_pressure']['systolic']} mmHg",
        delta=f"{vitals['blood_pressure']['systolic'] - round(yesterday['blood_pressure_systolic_avg'])} mmHg",
        delta_color="inverse",
    )
    d4.metric(
        "🚶 今日步數",
        f"{vitals['steps']:,} 步",
        delta=f"{vitals['steps'] - yesterday['steps']:+,}",
    )

    st.divider()
    st.subheader("📈 近 30 天生理趨勢")
    st.caption("虛線為警報閾值：🔴 紅色 = 危險上/下限，🟠 橘色 = 警示下限")
    fig = build_trend_chart(history, th)
    st.plotly_chart(fig, use_container_width=True)
