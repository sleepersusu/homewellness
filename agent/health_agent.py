# agent/health_agent.py  — CareAgent orchestrator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from agent.tools import get_vitals, get_sleep_report, get_medication_schedule
from agent.prompts import build_care_prompt
from agent.memory import wrap_with_memory

load_dotenv()


def build_agent():
    """Build the full multi-agent system.

    Initialises AnalysisAgent and AlertAgent, wraps them as tools,
    then builds the CareAgent (main orchestrator) with all five tools.
    """
    from agent.analysis_agent import build_analysis_agent, invoke_analysis_agent
    from agent.alert_agent import build_alert_agent, invoke_alert_agent

    analysis_graph = build_analysis_agent()
    alert_graph = build_alert_agent()

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

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    graph = create_agent(llm, tools=main_tools, system_prompt=build_care_prompt())
    return wrap_with_memory(graph)


def invoke_agent(agent_with_memory, user_input: str, session_id: str = "default") -> str:
    """Invoke the CareAgent and return the text response."""
    result = agent_with_memory.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    return result["output"]
