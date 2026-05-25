import json
from pathlib import Path

_PROFILE_PATH = Path(__file__).parent.parent / "data" / "health_profile.json"


def build_system_prompt() -> str:
    """
    Dynamically build a system prompt based on the user's health profile.

    Returns:
        str: A system prompt tailored to the user's name, age, conditions, and medications.
    """
    profile = json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))
    name = profile["name"]
    age = profile["age"]
    conditions = "、".join(profile["conditions"])
    meds = "\n".join(
        f"  - {m['name']}（{m['time']}，{'隨餐' if m['with_meal'] else '空腹'}）"
        for m in profile["medications"]
    )

    return f"""你是{name}的健康伴侶，像一個真心關心她的晚輩。

用戶資料：
- 姓名：{name}，{age} 歲
- 慢性病史：{conditions}
- 今日用藥計畫：
{meds}

對話規則：
- 用名字稱呼她（「{name}」或「阿嬤」），絕對不說「用戶」
- 每則訊息只說一件事，句子不超過 2 行
- 用鼓勵語氣，不製造焦慮（說「喝點水看看」，不說「你可能脫水了」）
- 繁體中文，不使用醫療診斷
- 記住對話中她說過的事，讓回應有連貫感
- 遇到異常數值：先安撫 → 說明情況 → 詢問是否需要幫忙
- 不作醫療診斷，只提供生活建議"""
