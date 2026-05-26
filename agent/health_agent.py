# agent/health_agent.py  — CareAgent orchestrator
import time
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from agent.llm_factory import get_llm
from agent.tools import get_vitals, get_sleep_report, get_medication_schedule
from agent.prompts import build_care_prompt
from agent.memory import wrap_with_memory

# USD per 1M tokens (input / output)
_MODEL_PRICES: dict[str, dict[str, float]] = {
    "gpt-4o-mini":            {"input": 0.15,   "output": 0.60},
    "gpt-4o":                 {"input": 2.50,   "output": 10.00},
    "gpt-4.1-mini":           {"input": 0.40,   "output": 1.60},
    "gpt-4.1":                {"input": 2.00,   "output": 8.00},
    "gemini-2.5-flash-lite":  {"input": 0.04,   "output": 0.16},
    "gemini-2.5-flash":       {"input": 0.075,  "output": 0.30},
    "gemini-2.5-pro":         {"input": 1.25,   "output": 10.00},
}


def _compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    prices = _MODEL_PRICES.get(model, {"input": 0.0, "output": 0.0})
    return (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000

load_dotenv()

DEFAULT_CARE_MODEL = "gpt-4o-mini"
DEFAULT_ANALYSIS_MODEL = "gemini-2.5-flash"
DEFAULT_ALERT_MODEL = "gpt-4o-mini"


def build_agent(
    care_model: str = DEFAULT_CARE_MODEL,
    analysis_model: str = DEFAULT_ANALYSIS_MODEL,
    alert_model: str = DEFAULT_ALERT_MODEL,
):
    """Build the full multi-agent system.

    Accepts model names for each agent so the Streamlit UI can swap
    models without restarting the server.
    """
    from agent.analysis_agent import build_analysis_agent, invoke_analysis_agent
    from agent.alert_agent import build_alert_agent, invoke_alert_agent

    analysis_graph = build_analysis_agent(model=analysis_model)
    alert_graph = build_alert_agent(model=alert_model)

    @tool
    def call_analysis_agent(query: str) -> str:
        """委派給健康數據分析專家。
        當用戶詢問近期健康趨勢、週報分析或需要深度數據解讀時呼叫。
        輸入：具體的分析請求（例如「近7天心率趨勢」）。"""
        return invoke_analysis_agent(analysis_graph, query)

    @tool
    def call_alert_agent(situation: str) -> str:
        """委派給緊急應變專家。
        當偵測到生理數值異常或用戶描述緊急症狀時呼叫。
        輸入：異常情況描述（例如「心率125 bpm，血氧88%」）。"""
        return invoke_alert_agent(alert_graph, situation)

    main_tools = [
        get_vitals,
        get_sleep_report,
        get_medication_schedule,
        call_analysis_agent,
        call_alert_agent,
    ]

    llm = get_llm(care_model)
    graph = create_agent(llm, tools=main_tools, system_prompt=build_care_prompt())
    return wrap_with_memory(graph)


def invoke_agent(
    agent_with_memory,
    user_input: str,
    session_id: str = "default",
    model: str = DEFAULT_CARE_MODEL,
) -> tuple[str, dict]:
    """Invoke the CareAgent and return (text, stats) tuple.

    stats keys: latency (s), input_tokens, output_tokens, total_tokens, cost_usd, model.
    """
    t0 = time.time()
    result = agent_with_memory.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    latency = time.time() - t0

    usage = result.get("usage_metadata", {})
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    stats: dict = {
        "latency": round(latency, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": usage.get("total_tokens", input_tokens + output_tokens),
        "cost_usd": _compute_cost(model, input_tokens, output_tokens),
        "model": model,
    }
    return result["output"], stats
