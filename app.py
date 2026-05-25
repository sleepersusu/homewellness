# app.py
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from agent.health_agent import build_agent, invoke_agent
from data.mock_sensors import (
    get_mock_vitals,
    get_mock_sleep_report,
    set_simulate_abnormal,
)

load_dotenv()

st.set_page_config(
    page_title="HomeWellness Companion",
    page_icon="🏥",
    layout="wide",
)

# ── Session State Init ────────────────────────────────
if "agent" not in st.session_state:
    with st.spinner("載入 AI 健康伴侶..."):
        st.session_state.agent = build_agent()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "simulate_abnormal" not in st.session_state:
    st.session_state.simulate_abnormal = False
if "pending_proactive" not in st.session_state:
    st.session_state.pending_proactive = None

# ── APScheduler Heartbeat ─────────────────────────────
from apscheduler.schedulers.background import BackgroundScheduler

if "scheduler_started" not in st.session_state:
    def _proactive_monitor():
        vitals = get_mock_vitals()
        thresholds = json.loads(
            Path("data/health_profile.json").read_text(encoding="utf-8")
        )["alert_thresholds"]
        if (
            vitals["heart_rate"] > thresholds["heart_rate_high"]
            or vitals["spo2"] < thresholds["spo2_low"]
        ):
            st.session_state["pending_proactive"] = (
                f"（系統觸發）偵測到異常數值：心率 {vitals['heart_rate']} bpm，"
                f"血氧 {vitals['spo2']}%，請立即關心陳阿嬤。"
            )

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_proactive_monitor, "interval", seconds=5)
    _scheduler.start()
    st.session_state.scheduler_started = True

# ── Handle Proactive Trigger ──────────────────────────
if st.session_state.pending_proactive:
    _msg = st.session_state.pending_proactive
    st.session_state.pending_proactive = None
    with st.spinner("Agent 偵測到異常..."):
        _resp = invoke_agent(st.session_state.agent, _msg)
    st.session_state.messages.append({"role": "assistant", "content": _resp})
    st.rerun()

# ── Layout ────────────────────────────────────────────
st.title("🏥 HomeWellness Companion")
col_data, col_chat = st.columns([1, 2])

# Left: Data Panel
with col_data:
    vitals = get_mock_vitals()
    sleep = get_mock_sleep_report()
    profile = json.loads(Path("data/health_profile.json").read_text(encoding="utf-8"))

    st.subheader("📊 即時生理數據")
    hr = vitals["heart_rate"]
    spo2 = vitals["spo2"]
    st.metric("💓 心率", f"{hr} bpm", "⚠️ 異常" if hr > 120 or hr < 50 else "正常")
    st.metric("🩸 血氧", f"{spo2}%", "⚠️ 異常" if spo2 < 90 else "正常")
    st.metric("😴 昨晚睡眠", f"{sleep['total_hours']} hrs")
    st.metric("🌡️ 環境溫度", f"{vitals['temperature']}°C")

    st.divider()
    st.subheader("💊 今日用藥")
    for med in profile["medications"]:
        st.write(f"⏰ {med['time']} — {med['name']}")

    st.divider()
    st.subheader("🎮 Demo 控制台")

    if st.button("🌅 模擬早晨問候", use_container_width=True):
        prompt = (
            "（系統觸發）現在是早上8點，請主動問候陳阿嬤，"
            "分享昨晚睡眠報告，並提醒早餐後服用降血壓藥。"
        )
        with st.spinner("Agent 思考中..."):
            response = invoke_agent(st.session_state.agent, prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🚨 模擬心率異常（125 bpm）", use_container_width=True):
        set_simulate_abnormal(True)
        st.session_state.simulate_abnormal = True
        prompt = (
            "（系統觸發）偵測到心率 125 bpm，血氧 88%，"
            "請立即關心陳阿嬤，並觸發緊急通報流程。"
        )
        with st.spinner("Agent 處理中..."):
            response = invoke_agent(st.session_state.agent, prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.session_state.simulate_abnormal:
        if st.button("🔄 恢復正常數值", use_container_width=True):
            set_simulate_abnormal(False)
            st.session_state.simulate_abnormal = False
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
            response = invoke_agent(st.session_state.agent, user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
