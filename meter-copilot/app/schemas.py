"""请求与响应模型。"""
from typing import Literal

from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    question: str = Field(..., min_length=2, description="自然语言问题，建议包含台区编号如 TQ-10086")


class DistrictMetrics(BaseModel):
    latest_success_rate: float | None = None
    stat_date: str | None = None
    stop_collect_count: int = 0
    clock_error_count: int = 0
    meter_count: int = 0


class DiagnoseResponse(BaseModel):
    district_id: str | None = None
    summary: str
    health_level: Literal["normal", "warning", "critical", "unknown"]
    metrics: DistrictMetrics | None = None
    possible_causes: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    llm_mode: Literal["mock", "live"] = "mock"
    message: str | None = Field(default=None, description="无法诊断时的提示")
