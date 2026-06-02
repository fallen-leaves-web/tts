# 表计采集健康小助手（Meter Health Copilot）v0.1

边做边学用的第一个小项目：用 **Mock 计量数据 + 大模型** 生成结构化运行健康诊断报告。

详细设计见：[docs/项目设计-表计采集健康小助手.md](../docs/项目设计-表计采集健康小助手.md)

## 快速开始

```bash
cd meter-copilot
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 无 API Key 也可运行（Mock 模式）

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

浏览器打开：http://127.0.0.1:8000/docs

## 测试

```bash
curl -s -X POST http://127.0.0.1:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{"question":"台区 TQ-10086 采集成功率下降可能什么原因？"}' | python -m json.tool
```

Mock 库台区：

| 台区 ID | 说明 |
|---------|------|
| TQ-10001 | 正常，成功率约 98% |
| TQ-10086 | 异常，成功率约 72%，多块停抄/时钟异常 |

## 接入真实大模型

在 `.env` 中配置（OpenAI 兼容接口均可）：

```
LLM_API_KEY=你的密钥
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_MOCK=false
```

## v0.1 学什么

- FastAPI + Pydantic
- SQLite 查询与业务 Mock
- Prompt 与 JSON 结构化输出
- 「有数据再让模型说话」防幻觉

下一步 v0.2：在 `data/faq/` 增加规程 RAG。
