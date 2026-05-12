---
name: phys-report-gen
description: 'Use when: generating physics experiment reports, creating HTML reports with MathJax and Chart.js, writing 暨南大学 standard format experiment reports, converting data to formatted tables, creating lab report documents with proper structure (目的/原理/仪器/步骤/数据/分析/讨论/思考题), LaTeX formula rendering in reports. Keywords: 实验报告, HTML报告, 生成报告, 物理实验报告, 报告模板, MathJax, Chart.js'
argument-hint: '实验名称或文件夹'
---

# 物理实验报告生成

## When to Use
- 根据实验数据自动生成标准格式的实验报告
- 创建 HTML 网页版报告（含 MathJax 公式 + Chart.js 图表）
- 生成 Markdown 草稿后转为 Word/PDF
- 填写暨南大学标准 8 段式实验报告

## Report Structure (暨南大学模板 — 严格遵循 `实验报告模版.docx`)

```
暨南大学 物理实验报告
实验项目：
姓名 学号 日期

【实验目的】
(陈述实验要解决的科学问题，体现实验核心目标)

【实验仪器与用具】
（给出详细参数）

【实验原理】
（使用自己的语言说明，给出公式。可以给出原理图，无需绘制设备图）

【实验要求及数据记录】
（简要说明操作步骤）
（给出详细数据记录表格）

【数据处理及图形】
（简要说明处理过程，给出计算过程；如需要，给出不确定度及图形）

【结果分析及讨论】
（汇报实验结论，分析实验误差，提出改进建议）
```

## ⚠️ 关键规则

### 数据确认（CRITICAL）
**在开始撰写报告前，必须将原始数据展示给用户确认。**
- 从 .txt 文件中提取的数据 → 汇总展示 → 等待用户确认 "数据正确"
- 用户直接提供的数值数据 → 整理为表格 → 等待用户确认
- 未经确认的数据不得填入报告

### 实验书原文处理（用户提供已提取文本）
用户使用外部工具提取实验书内容后提供。AI 需：
- **实验目的**：根据用户提供的原文，按模板要求精炼为科学问题陈述
- **实验仪器与用具**：根据用户提供的原文，保持详细参数，整理为列表
- **实验原理**：根据用户提供的原文，**用自己的话重新阐述**（不能照抄），给出公式
- **实验步骤**：根据用户提供的原文，简要说明操作步骤
- 如需原理图/示意图 → **提示用户提供图片**
- ⚠️ **禁止使用 view_image 对书本文字做 OCR**（不准确、有误导）

### 用户输入格式
```
【实验目的】
(用户从书本提取的原文)

【实验仪器与用具】
(用户从书本提取的原文)

【实验原理】
(用户从书本提取的原文，含公式)

【实验步骤】
(用户从书本提取的原文)
```
AI 收到后先确认理解无误，再精炼和重写。

### .docx 生成
- 使用 `python-docx` 基于 `实验报告模版.docx` 精确填充
- 读取模板用 MarkItDown MCP
- **禁止修改模板格式**

## HTML Template

参考 `html/迈克尔逊.html` 和 `html/双棱镜.html` 的样式：

### 必须引入的资源
```html
<!-- MathJax 数学公式渲染 -->
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js" async></script>
<!-- Chart.js 图表 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### 设计规范
- 配色：以 `#2c7da0`（深蓝绿）为主色调
- 字体：`'Segoe UI', 'Georgia', 'Times New Roman', serif`
- 背景：`#eef2f5`，报告卡片：白色 + 阴影
- 响应式：最大宽度 1000-1200px，移动端适配
- 表格：边框 `#cbd5e1`，表头 `#e9edf2`
- 打印友好：`@media print` 调整

### Markdown 草稿模板

报告草稿先用 Markdown 写，方便后续导出：

```markdown
# 实验名称

**暨南大学 物理实验报告**

| 项目 | 内容 |
|------|------|
| 姓名 | ___ |
| 学号 | ___ |
| 日期 | ___ |

## 一、实验目的
...

## 二、实验原理
$$公式$$

## 三、实验仪器
- 

## 四、实验步骤
1. 

## 五、实验数据
| 表头 | ... |
|------|-----|

## 六、数据处理与分析
### 6.1 峰值提取
### 6.2 扩散长度计算
### 6.3 误差分析

## 七、实验结果与讨论

## 八、思考题
```

## Chart.js 集成

```html
<div class="chart-container">
    <canvas id="decayChart"></canvas>
</div>
<script>
new Chart(document.getElementById('decayChart'), {
    type: 'scatter',
    data: {
        datasets: [{
            label: '实验数据',
            data: [{x: pos, y: current}, ...],
            pointBackgroundColor: '#2c7da0'
        }, {
            label: '指数拟合',
            data: [...],
            type: 'line',
            borderColor: '#e76f51'
        }]
    },
    options: {
        scales: {
            x: { title: { display: true, text: '位置 (μm)' } },
            y: { title: { display: true, text: '电流 (μA)' } }
        }
    }
});
</script>
```

## Procedure

1. 收集实验原始数据和计算结果
2. 用 Markdown 撰写报告草稿
3. 如需 HTML 版本，套用 `html/迈克尔逊.html` 模板样式
4. 嵌入 MathJax 公式和 Chart.js 图表
5. 导出为 `实验报告.html` 或用浏览器打印为 PDF
