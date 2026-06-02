# 在本机 G:\ 创建项目

云环境无法直接写入你电脑的 `G:\`，请在你本机 **Windows** 上按下面任选一种方式操作。

---

## 方式一：一键脚本（推荐）

### 1. 下载安装脚本

在 PowerShell 中执行（会把脚本保存到 `G:\`）：

```powershell
# 若无法访问 GitHub，可让同事从仓库复制 setup-windows.ps1 到 G:\
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/fallen-leaves-web/tts/cursor/meter-copilot-v01-5efe/meter-copilot/setup-windows.ps1" -OutFile "G:\setup-windows.ps1"
```

若 raw 地址不可用，可手动从仓库 `meter-copilot/setup-windows.ps1` 复制到 `G:\setup-windows.ps1`。

### 2. 运行脚本（默认安装到 G:\meter-copilot）

```powershell
Set-ExecutionPolicy -Scope Process Bypass
cd G:\
.\setup-windows.ps1
```

指定其它目录：

```powershell
.\setup-windows.ps1 -TargetDir "G:\meter-copilot"
```

### 3. 启动项目

```powershell
cd G:\meter-copilot
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

浏览器访问：http://127.0.0.1:8000/docs

---

## 方式二：Git 克隆后复制

```powershell
cd G:\
git clone -b cursor/meter-copilot-v01-5efe --depth 1 https://github.com/fallen-leaves-web/tts.git tts-temp
xcopy /E /I tts-temp\meter-copilot meter-copilot
rmdir /S /Q tts-temp

cd G:\meter-copilot
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

---

## 方式三：只在 G:\ 新建空目录后拷贝

1. 资源管理器创建文件夹：`G:\meter-copilot`
2. 从已 clone 的仓库或云代理仓库，把整个 `meter-copilot` 文件夹**复制**进去（含 `app`、`requirements.txt` 等）
3. 在 `G:\meter-copilot` 打开终端，执行方式二里 `cd` 之后的命令

---

## 安装后目录结构

```
G:\meter-copilot\
├── app\
├── requirements.txt
├── .env.example
├── .env                 ← 运行脚本后生成
├── .venv\               ← 虚拟环境
├── meter_mock.db        ← 首次启动后自动生成
└── README.md
```

---

## 常见问题

| 问题 | 处理 |
|------|------|
| `python` 不是内部命令 | 安装 Python 3.11+，勾选 **Add to PATH**，或使用 `py -3` |
| 无法运行 ps1 | `Set-ExecutionPolicy -Scope Process Bypass` |
| `uvicorn` 找不到 | 先 `.\.venv\Scripts\activate` 再运行 |
| 想接真实大模型 | 编辑 `G:\meter-copilot\.env` 填写 `LLM_API_KEY` 等 |

---

## 测试

```powershell
curl -X POST http://127.0.0.1:8000/diagnose -H "Content-Type: application/json" -d "{\"question\":\"台区 TQ-10086 采集成功率下降可能什么原因？\"}"
```

或在 Swagger 页面 `/docs` 里测试 `POST /diagnose`。
