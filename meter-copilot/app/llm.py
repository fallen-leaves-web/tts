"""大模型调用：支持 OpenAI 兼容 API；无 Key 时使用 Mock。"""
from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

PROMPT_PATH = Path(__file__).parent / "prompts" / "diagnose_system.txt"


def _load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def use_mock_mode() -> bool:
    if os.getenv("LLM_MOCK", "").lower() in ("1", "true", "yes"):
        return True
    return not os.getenv("LLM_API_KEY", "").strip()


def mock_diagnose(snapshot: dict) -> dict:
    """无 API 时的规则 Mock，便于边做边学、离线调试。"""
    latest = snapshot.get("latest") or {}
    rate = latest.get("success_rate")
    stop_n = snapshot.get("stop_collect_count", 0)
    clock_n = snapshot.get("clock_error_count", 0)

    if rate is None:
        level = "unknown"
    elif rate < 0.85 or stop_n >= 5:
        level = "critical"
    elif rate < 0.95 or stop_n > 0 or clock_n > 0:
        level = "warning"
    else:
        level = "normal"

    date = latest.get("stat_date", "未知日期")
    rate_pct = f"{rate * 100:.1f}%" if rate is not None else "无"

    return {
        "summary": (
            f"台区 {snapshot['district_id']}（{snapshot['name']}）最新采集成功率 {rate_pct}，"
            f"停抄 {stop_n} 块、时钟异常 {clock_n} 块，综合判定为 {level}。"
        ),
        "health_level": level,
        "possible_causes": [
            "采集终端或通信信道不稳定导致日成功率下降",
            "部分电能表停抄或时钟超差未及时处理",
        ],
        "recommended_actions": [
            "核查该台区采集终端在线状态与信噪强度",
            "对停抄、时钟异常表计生成运维工单并现场处理",
            "对比前一日成功率，确认是否为突发下降",
        ],
        "evidence": [
            f"数据：{date} 采集成功率 {rate_pct}",
            f"数据：停抄表计 {stop_n} 块，时钟异常 {clock_n} 块",
            f"数据：台区挂表 {snapshot['meter_count']} 块",
        ],
    }


async def generate_diagnose_json(snapshot: dict) -> tuple[dict, str]:
    """
    根据台区快照生成诊断 JSON。
    返回 (解析后的 dict, llm_mode)。
    """
    if use_mock_mode():
        return mock_diagnose(snapshot), "mock"

    system = _load_system_prompt()
    user_content = (
        "用户问题：请根据以下系统查询结果，输出运行健康诊断 JSON。\n\n"
        f"系统查询结果：\n{json.dumps(snapshot, ensure_ascii=False, indent=2)}"
    )

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    api_key = os.getenv("LLM_API_KEY", "")

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

    data = json.loads(content)
    return data, "live"
