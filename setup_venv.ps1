# 物理实验报告 — 虚拟环境安装脚本
# 用法：右键 → "使用 PowerShell 运行" 或在终端执行 .\setup_venv.ps1

param(
    [string]$VenvPath = "E:\python-venvs\physics-experiment",
    [switch]$Recreate = $false
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  暨南大学物理实验报告 — Python 环境安装" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 如果已存在且不强制重建
if (Test-Path $VenvPath) {
    if ($Recreate) {
        Write-Host "删除现有虚拟环境..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $VenvPath
    } else {
        Write-Host "虚拟环境已存在：$VenvPath" -ForegroundColor Green
        Write-Host "如需重建，请加 -Recreate 参数" -ForegroundColor Yellow
        Write-Host ""
        
        # 激活并安装/更新依赖
        $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
        if (Test-Path $ActivateScript) {
            & $ActivateScript
            pip install -r requirements.txt --quiet
            Write-Host "依赖已更新完成！" -ForegroundColor Green
        }
        return
    }
}

Write-Host "正在创建虚拟环境..." -ForegroundColor Yellow
Write-Host "  路径：$VenvPath" -ForegroundColor Gray

# 查找 Python
$pythonCmd = $null
foreach ($cmd in @("python3", "python")) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) {
        $pythonCmd = $cmd
        break
    }
}

if (-not $pythonCmd) {
    Write-Host "错误：未找到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    Write-Host "下载地址：https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "  Python：$( & $pythonCmd --version )" -ForegroundColor Gray
Write-Host "  路径：$( (Get-Command $pythonCmd).Source )" -ForegroundColor Gray

# 创建 venv
$parentDir = Split-Path $VenvPath -Parent
if (-not (Test-Path $parentDir)) {
    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
}

& $pythonCmd -m venv $VenvPath

if (-not (Test-Path $VenvPath)) {
    Write-Host "错误：虚拟环境创建失败" -ForegroundColor Red
    pause
    exit 1
}

# 激活并安装依赖
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
& $ActivateScript

Write-Host "正在安装依赖包..." -ForegroundColor Yellow
$reqFile = Join-Path $PSScriptRoot "requirements.txt"
pip install -r $reqFile

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "  虚拟环境：$VenvPath" -ForegroundColor Green
Write-Host "  激活命令：$VenvPath\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# 提示：在 VS Code 中选择此解释器
Write-Host "下一步：在 VS Code 中按 Ctrl+Shift+P，搜索" -ForegroundColor Cyan
Write-Host "  'Python: Select Interpreter'" -ForegroundColor White
Write-Host "  然后选择：" -ForegroundColor Cyan
Write-Host "  $VenvPath\Scripts\python.exe" -ForegroundColor White

pause
