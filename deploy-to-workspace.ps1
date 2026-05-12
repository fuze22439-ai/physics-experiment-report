# 物理实验报告 Skills/Agents 一键部署脚本
# 将 .github 配置复制到目标工作区
# 用法：.\deploy-to-workspace.ps1 -WorkspacePath "D:\新实验项目"
#       或拖拽目标文件夹到此脚本上

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspacePath,
    [switch]$VenvOnly = $false,
    [switch]$Minimal = $false
)

$SourceDir = Split-Path $PSScriptRoot -Parent
$SourceGithub = Join-Path $SourceDir ".github"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  物理实验报告 — 工作区部署" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 验证源
if (-not (Test-Path $SourceGithub)) {
    Write-Host "错误：未找到源配置 $SourceGithub" -ForegroundColor Red
    pause
    exit 1
}

# 验证目标
if (-not (Test-Path $WorkspacePath)) {
    Write-Host "目标路径不存在，是否创建？(Y/n) " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -eq '' -or $response -eq 'Y' -or $response -eq 'y') {
        New-Item -ItemType Directory -Path $WorkspacePath -Force | Out-Null
        Write-Host "已创建：$WorkspacePath" -ForegroundColor Green
    } else {
        exit 0
    }
}

if (-not $VenvOnly) {
    $TargetGithub = Join-Path $WorkspacePath ".github"
    
    if ($Minimal) {
        # 最小部署：仅 docx-editor Skill
        Write-Host "最小部署模式：仅 docx-editor Skill" -ForegroundColor Cyan
        $TargetSkills = Join-Path $TargetGithub "skills"
        New-Item -ItemType Directory -Force -Path $TargetSkills | Out-Null
        $SourceSkill = Join-Path $SourceGithub "skills\docx-editor"
        if (Test-Path $SourceSkill) {
            Copy-Item -Recurse $SourceSkill (Join-Path $TargetSkills "docx-editor") -Force
            Write-Host "  ✅ docx-editor Skill 已部署" -ForegroundColor Green
        }
        # 复制 copilot-instructions 的精简版
        $MinimalInstructions = @"
# Docx Editor

本工作区启用了 docx 编辑能力。

## 读取 docx
使用 MarkItDown MCP (`mcp_microsoft_mar_convert_to_markdown`)

## 编辑/填充 docx
- 简单替换：`python .github/skills/docx-editor/scripts/fill_template.py 模板.docx 输出.docx --replace '{"占位符":"内容"}'`
- Jinja2 模板：`python .github/skills/docx-editor/scripts/fill_template.py 模板.docx 输出.docx --jinja --data '{"key":"val"}'`
- Markdown转docx：`python .github/skills/docx-editor/scripts/md2docx.py input.md output.docx`

## Python 环境
共享虚拟环境：`E:\python-venvs\physics-experiment\Scripts\python.exe`
依赖：python-docx, docxtpl
"@
        New-Item -ItemType Directory -Force -Path $TargetGithub | Out-Null
        $MinimalInstructions | Out-File -FilePath (Join-Path $TargetGithub "copilot-instructions.md") -Encoding UTF8
        Write-Host "  ✅ 最小化配置已写入" -ForegroundColor Green
    } else {
        # 完整部署：所有 Skills + Agents
        if (Test-Path $TargetGithub) {
            Write-Host "目标已存在 .github 文件夹，选择操作：" -ForegroundColor Yellow
            Write-Host "  [M] 合并（保留目标已有文件）" -ForegroundColor White
            Write-Host "  [R] 替换（完全覆盖）" -ForegroundColor White
            Write-Host "  [S] 跳过" -ForegroundColor White
            $choice = Read-Host
            switch ($choice.ToUpper()) {
                'R' {
                    Remove-Item -Recurse -Force $TargetGithub
                    Copy-Item -Recurse $SourceGithub $TargetGithub
                }
                'M' {
                    Copy-Item -Recurse $SourceGithub\* $TargetGithub -Force
                }
                'S' { Write-Host "跳过 .github 部署" -ForegroundColor Gray }
                default { Write-Host "无效选择，跳过" -ForegroundColor Gray }
            }
        } else {
            Copy-Item -Recurse $SourceGithub $TargetGithub
            Write-Host "已部署 .github/ → $TargetGithub" -ForegroundColor Green
        }
    }
}

# 部署虚拟环境（默认共享 E:\python-venvs\physics-experiment）
$VenvPath = "E:\python-venvs\physics-experiment"
Write-Host ""
Write-Host "虚拟环境配置：" -ForegroundColor Cyan
Write-Host "  共享路径：$VenvPath" -ForegroundColor Gray
Write-Host "  所有物理实验工作区共用此虚拟环境" -ForegroundColor Gray

if (Test-Path $VenvPath) {
    Write-Host "  状态：已安装 ✓" -ForegroundColor Green
} else {
    Write-Host "  状态：未安装，请先运行 setup_venv.ps1" -ForegroundColor Yellow
}

# 复制 requirements.txt 到目标工作区
$ReqSource = Join-Path $SourceDir "requirements.txt"
if (Test-Path $ReqSource) {
    Copy-Item $ReqSource (Join-Path $WorkspacePath "requirements.txt") -Force
    Write-Host "  已复制 requirements.txt" -ForegroundColor Green
}

# 复制 setup_venv.ps1 到目标工作区
$SetupSource = Join-Path $SourceDir "setup_venv.ps1"
if (Test-Path $SetupSource) {
    Copy-Item $SetupSource (Join-Path $WorkspacePath "setup_venv.ps1") -Force
    Write-Host "  已复制 setup_venv.ps1" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "  工作区：$WorkspacePath" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "后续步骤：" -ForegroundColor Cyan
Write-Host "  1. 在 VS Code 中打开工作区：$WorkspacePath" -ForegroundColor White
Write-Host "  2. 如需新实验，运行 setup_venv.ps1 安装 Python 依赖" -ForegroundColor White
Write-Host "  3. 在聊天中尝试 /phys-data-process 等命令" -ForegroundColor White

pause
