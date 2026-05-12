---
name: docx-editor
description: 'Use when: reading, creating, editing, or filling .docx Word documents; generating reports from templates; converting docx to markdown; filling placeholder fields in Word templates; batch generating documents. Keywords: docx, word, 文档, 报告, 模板, template, report, python-docx, docxtpl'
argument-hint: '模板路径 或 "生成报告"'
---

# Docx Editor — 轻量级 Word 文档编辑器

纯 docx 编辑能力，无物理实验依赖，可丢入任何工作区使用。

## 依赖

```bash
pip install python-docx docxtpl
```

所有操作通过 E 盘共享虚拟环境：
```
E:\python-venvs\physics-experiment\Scripts\python.exe
```

## When to Use
- 读取 .docx 内容 → 用 MarkItDown MCP 一键转 Markdown
- 填充 Word 模板 → 用 python-docx / docxtpl
- 从 Markdown 生成 .docx → 用 python-docx 编程构建
- 批量生成文档 → 循环调用 docxtpl

## Tool Choice

| 任务 | 工具 | 说明 |
|------|------|------|
| **读取 docx** | `mcp_microsoft_mar_convert_to_markdown` | 一行调用，零代码 |
| **填充模板（文本替换）** | python-docx | 遍历段落/run 替换 |
| **填充模板（复杂数据）** | docxtpl + Jinja2 | 表格、循环、条件 |
| **从头创建 docx** | python-docx | 编程构建结构 |

## Procedure

### 1. 读取 docx 内容
```
mcp_microsoft_mar_convert_to_markdown:
  uri: "file:///E:/path/to/file.docx"
```

### 2. 填充模板（简单文本替换）

```python
from docx import Document
doc = Document("模板.docx")
for p in doc.paragraphs:
    if "【实验目的】" in p.text:
        # 替换当前段落或在其后插入
        p.text = p.text.replace("(陈述...)", "1. 掌握...方法")
doc.save("输出.docx")
```

### 3. 填充模板（使用 Jinja2 标签）

先在模板中写入 `{{ variable }}` 标签，然后用 docxtpl 渲染：

```python
from docxtpl import DocxTemplate
doc = DocxTemplate("模板.docx")
doc.render({
    "title": "扫描光电流实验",
    "name": "张三",
    "date": "5月12日"
})
doc.save("报告.docx")
```

### 4. 从 Markdown 生成 docx

```python
from docx import Document
from docx.shared import Pt
doc = Document()
# 设置默认字体
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)
# 逐行解析 markdown 添加段落
for line in markdown_content.split('\n'):
    doc.add_paragraph(line)
doc.save("output.docx")
```

## Scripts

- [fill_template.py](./scripts/fill_template.py) — 通用模板填充脚本
- [md2docx.py](./scripts/md2docx.py) — Markdown 转 docx

## Constraints
- 不修改模板原文的字体、边距、样式
- 表格数据保留原始精度
- 生成后提示用户验证格式
