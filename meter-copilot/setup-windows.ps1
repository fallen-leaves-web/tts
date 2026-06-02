# 在 Windows 本机安装「表计采集健康小助手」到指定目录（默认 G:\meter-copilot）
# 用法（PowerShell）：
#   Set-ExecutionPolicy -Scope Process Bypass
#   cd <任意目录>
#   .\setup-windows.ps1
# 或指定路径：
#   .\setup-windows.ps1 -TargetDir "G:\meter-copilot"

param(
    [string]$TargetDir = "G:\meter-copilot",
    [string]$Branch = "cursor/meter-copilot-v01-5efe",
    [string]$RepoUrl = "https://github.com/fallen-leaves-web/tts.git"
)

$ErrorActionPreference = "Stop"

Write-Host "==> 目标目录: $TargetDir" -ForegroundColor Cyan

# 检查 Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
    if ($python) {
        $pythonCmd = "py -3"
    } else {
        Write-Host "未找到 Python。请先安装 Python 3.11+ 并勾选 Add to PATH。" -ForegroundColor Red
        exit 1
    }
} else {
    $pythonCmd = "python"
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "未找到 Git。请安装 Git for Windows: https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

$parent = Split-Path -Parent $TargetDir
if ($parent -and -not (Test-Path $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}

$tempClone = Join-Path $env:TEMP ("tts-clone-" + [guid]::NewGuid().ToString("n").Substring(0, 8))

try {
    Write-Host "==> 从 GitHub 拉取分支 $Branch ..." -ForegroundColor Cyan
    git clone --branch $Branch --depth 1 $RepoUrl $tempClone

    $source = Join-Path $tempClone "meter-copilot"
    if (-not (Test-Path $source)) {
        throw "仓库中未找到 meter-copilot 目录，请确认分支 $Branch 是否正确。"
    }

    if (Test-Path $TargetDir) {
        Write-Host "==> 目录已存在，将覆盖更新（保留 .env）" -ForegroundColor Yellow
        $envBackup = Join-Path $env:TEMP "meter-copilot-env-backup"
        if (Test-Path (Join-Path $TargetDir ".env")) {
            Copy-Item (Join-Path $TargetDir ".env") $envBackup -Force
        }
        Remove-Item $TargetDir -Recurse -Force
    }

    Copy-Item $source $TargetDir -Recurse -Force

    if (Test-Path $envBackup) {
        Copy-Item $envBackup (Join-Path $TargetDir ".env") -Force
    }
} finally {
    if (Test-Path $tempClone) {
        Remove-Item $tempClone -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Set-Location $TargetDir

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "==> 已创建 .env（默认 Mock 模式，无需 API Key）" -ForegroundColor Green
}

Write-Host "==> 创建虚拟环境并安装依赖 ..." -ForegroundColor Cyan
if ($pythonCmd -eq "python") {
    python -m venv .venv
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\pip install -r requirements.txt
} else {
    py -3 -m venv .venv
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\pip install -r requirements.txt
}

Write-Host ""
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "项目位置: $TargetDir" -ForegroundColor Green
Write-Host ""
Write-Host "启动命令：" -ForegroundColor Cyan
Write-Host "  cd $TargetDir"
Write-Host "  .\.venv\Scripts\activate"
Write-Host "  uvicorn app.main:app --reload"
Write-Host ""
Write-Host "浏览器打开: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
