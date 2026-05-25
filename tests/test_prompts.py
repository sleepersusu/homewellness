from agent.prompts import build_care_prompt, build_analysis_prompt, build_alert_prompt


def test_prompt_contains_name():
    assert "陳阿嬤" in build_care_prompt()


def test_prompt_contains_conditions():
    prompt = build_care_prompt()
    assert "高血壓" in prompt
    assert "輕度糖尿病" in prompt


def test_prompt_contains_medication_time():
    prompt = build_care_prompt()
    assert "08:00" in prompt


def test_prompt_contains_behavior_rules():
    prompt = build_care_prompt()
    assert "繁體中文" in prompt
    assert "醫療診斷" in prompt


def test_analysis_prompt_contains_thresholds():
    prompt = build_analysis_prompt()
    assert "120" in prompt  # heart_rate_high threshold
    assert "90" in prompt   # spo2_low threshold


def test_alert_prompt_contains_contact():
    prompt = build_alert_prompt()
    assert "陳大文" in prompt
    assert "0912-345-678" in prompt
