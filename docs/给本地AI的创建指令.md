# 复制给「本机对话 AI」的创建指令

> 用法：把下面「---开始---」到「---结束---」整段复制，粘贴给你本地的 Cursor / ChatGPT / Copilot 等，并说明：**请在我电脑上执行，项目目录为 G:\meter-copilot**。

---开始---

你是一个在本机 Windows 上操作的编程助手。请帮我在 **`G:\meter-copilot`** 创建完整可运行的 Python 项目「表计采集健康小助手 v0.1」，并验证能启动。

## 硬性要求

1. 项目根目录必须是：`G:\meter-copilot`（若 G 盘不存在则改用 `D:\meter-copilot` 并告诉我）。
2. 使用 **Python 3.11+**、**FastAPI**、**SQLite Mock 数据**、**无 API Key 时 Mock 模式**。
3. 所有源代码文件使用 **UTF-8** 编码；中文注释正常显示。
4. 创建全部文件后执行：创建 venv、pip install、copy .env、启动 uvicorn、用 curl 或等价方式测试 `POST /diagnose`。
5. 完成后列出：创建了哪些文件、测试命令输出、`health_level` 是否为 `critical`（台区 TQ-10086）。

## 目录结构

```
G:\meter-copilot\
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
├── README.md
└── app\
    ├── __init__.py
    ├── main.py
    ├── schemas.py
    ├── db.py
    ├── extractor.py
    ├── llm.py
    ├── diagnose.py
    └── prompts\
        └── diagnose_system.txt
```

## 功能说明

- `GET /health` 返回 ok
- `POST /diagnose`  body: `{"question":"台区 TQ-10086 采集成功率下降可能什么原因？"}`
- 从问题中正则提取台区 ID（格式 `TQ-数字`）
- 查 SQLite：台区 TQ-10001 正常(98%)，TQ-10086 异常(72%)，含停抄/时钟异常表计
- 无 `LLM_API_KEY` 时走 `llm.py` 的 mock_diagnose，返回 `llm_mode: mock`
- 有 Key 且 `LLM_MOCK=false` 时调用 OpenAI 兼容 chat/completions

## 备选：若可访问 Git，优先克隆

```powershell
git clone -b cursor/meter-copilot-v01-5efe --depth 1 https://github.com/fallen-leaves-web/tts.git G:\tts-temp
xcopy /E /I /Y G:\tts-temp\meter-copilot G:\meter-copilot
rmdir /S /Q G:\tts-temp
```

克隆成功后只需 `cd G:\meter-copilot`、建 venv、pip install、copy .env、启动测试，**不必手写全部代码**。

若 Git 不可用，则按下列内容**逐文件创建**（内容必须一致）。

---

### requirements.txt

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.9.0
pydantic-settings>=2.6.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

### .env.example 与 .env（内容相同，.env 由复制得到）

```
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_MOCK=false
```

### .gitignore

```
.venv/
__pycache__/
*.pyc
.env
meter_mock.db
.pytest_cache/
```

### app/__init__.py

```python
# meter-copilot application package
```

### app/schemas.py

（完整代码见仓库 `meter-copilot/app/schemas.py`，包含 DiagnoseRequest、DistrictMetrics、DiagnoseResponse）

### app/extractor.py

正则 `\b(TQ-\d{4,6})\b` 提取台区 ID，转大写。

### app/db.py

- DB 路径：`Path(__file__).parent.parent / "meter_mock.db"`
- 表：districts, meters, collect_daily
- init_db 种子：TQ-10001 正常，TQ-10086 成功率 0.72，3 块 stop_collect，1 块 clock_error
- fetch_district_snapshot(district_id) 返回 dict

### app/prompts/diagnose_system.txt

电力计量采集诊断助手系统提示，要求只根据系统查询结果输出 JSON，禁止编造，字段含 summary、health_level、possible_causes、recommended_actions、evidence。

### app/llm.py

- use_mock_mode：无 LLM_API_KEY 或 LLM_MOCK=true 时用 mock
- mock_diagnose 按成功率与停抄数判定 normal/warning/critical
- generate_diagnose_json 异步调用 OpenAI 兼容 API，response_format json_object

### app/diagnose.py

run_diagnose：提取 ID → 查库 → llm → DiagnoseResponse

### app/main.py

FastAPI lifespan 调用 db.init_db；路由 /health、/diagnose

---

## 安装与验证命令（PowerShell）

```powershell
cd G:\meter-copilot
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

另开终端测试：

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/diagnose" -ContentType "application/json" -Body '{"question":"台区 TQ-10086 采集成功率下降可能什么原因？"}'
```

期望：`health_level` 为 `critical`，`latest_success_rate` 约 `0.72`。

---结束---
