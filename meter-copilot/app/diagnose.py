"""诊断编排：提取台区 → 查库 → 调 LLM → 组装响应。"""
from __future__ import annotations

from app import db, extractor, llm
from app.schemas import DiagnoseRequest, DiagnoseResponse, DistrictMetrics


async def run_diagnose(req: DiagnoseRequest) -> DiagnoseResponse:
    district_id = extractor.extract_district_id(req.question)
    if not district_id:
        return DiagnoseResponse(
            summary="未识别出台区编号",
            health_level="unknown",
            message="请在问题中包含台区编号，例如：台区 TQ-10086 采集成功率下降可能什么原因？",
            llm_mode="mock",
        )

    snapshot = db.fetch_district_snapshot(district_id)
    if not snapshot:
        return DiagnoseResponse(
            district_id=district_id,
            summary=f"未找到台区 {district_id} 的档案数据",
            health_level="unknown",
            message="Mock 库中仅包含 TQ-10001、TQ-10086，请换编号重试。",
            llm_mode="mock",
        )

    llm_json, mode = await llm.generate_diagnose_json(snapshot)
    latest = snapshot.get("latest") or {}

    metrics = DistrictMetrics(
        latest_success_rate=latest.get("success_rate"),
        stat_date=latest.get("stat_date"),
        stop_collect_count=snapshot.get("stop_collect_count", 0),
        clock_error_count=snapshot.get("clock_error_count", 0),
        meter_count=snapshot.get("meter_count", 0),
    )

    return DiagnoseResponse(
        district_id=district_id,
        summary=llm_json.get("summary", ""),
        health_level=llm_json.get("health_level", "unknown"),
        metrics=metrics,
        possible_causes=llm_json.get("possible_causes", []),
        recommended_actions=llm_json.get("recommended_actions", []),
        evidence=llm_json.get("evidence", []),
        llm_mode=mode,  # type: ignore[arg-type]
    )
