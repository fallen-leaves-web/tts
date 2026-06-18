"""表计采集健康小助手 v0.1 — FastAPI 入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import db
from app.diagnose import run_diagnose
from app.schemas import DiagnoseRequest, DiagnoseResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(
    title="Meter Health Copilot",
    description="表计采集健康小助手 v0.1 — 边做边学用 Mock 数据 + LLM 结构化诊断",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(req: DiagnoseRequest):
    return await run_diagnose(req)
