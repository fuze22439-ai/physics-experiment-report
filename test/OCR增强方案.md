# 实验书图片识别增强方案

> 调研时间：2026年5月 | 目标：将手机拍摄的书本照片提取为结构化 Markdown+LaTeX+表格

---

## 一、当前痛点

| 问题 | 现状 |
|------|------|
| 书本文字提取 | 依赖用户外部OCR → 手动整理 → 再发给AI |
| 公式识别 | 用户手动输入 LaTeX，费时易错 |
| 表格识别 | 手机拍表格 → AI 读取不准确 |
| 图片依赖 | `view_image` OCR 不可靠，已禁用 |

**目标**：端到端自动化 — 用户拍照 → 系统自动输出 `【实验目的】+【实验原理】+公式+表格`

---

## 二、推荐架构：三层流水线

```
手机拍照（书本页）
      │
      ▼
┌─────────────────────────────────┐
│ 第一层：图像预处理               │
│ • 透视校正 + 去阴影 + 对比度增强  │
│ • 区域分割：正文区/公式区/表格区   │
│ 工具：OpenCV + 自定义脚本        │
│ 成本：¥0                         │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│ 第二层：专项识别                 │
│ ┌──────────┬─────────┬────────┐ │
│ │ 正文区    │ 公式区   │ 表格区  │ │
│ │PaddleOCR │ MathPix │Paddle  │ │
│ │→ 中文文本│ → LaTeX │ → HTML │ │
│ └──────────┴─────────┴────────┘ │
│ 成本：正文/表格免费；公式 ~$0.02/个│
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│ 第三层：视觉LLM校验融合          │
│ • 输入：原图 + 第二层提取结果     │
│ • 任务：纠错 → 补漏 → 统一格式   │
│ • 推荐：通义千问VL（国内首选）    │
│ 成本：~¥0.003/页                 │
└──────────────┬──────────────────┘
               ▼
    结构化 Markdown + LaTeX 公式 + 表格
```

---

## 三、核心方案对比

| 方案 | 中文 | 公式 | 表格 | 国内直连 | 100页/月成本 |
|------|:--:|:--:|:--:|:--:|:--:|
| **通义千问VL 端到端** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ~¥0.5 |
| **豆包视觉API 端到端** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ~¥0.3 |
| **PaddleOCR + MathPix + 千问校验** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ~¥16 |
| GPT-4o 端到端 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌需代理 | ~$2 |
| PaddleOCR 纯本地 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ✅ | ¥0 |

---

## 四、推荐落地路径（分三阶段）

### 🚀 第一阶段：快速原型（2-4小时）

**纯通义千问VL 端到端** — 零部署，最快见效

```python
# 一条 API 调用即可
import requests
response = requests.post(
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "qwen-vl-plus",
        "input": {
            "messages": [{
                "role": "user",
                "content": [
                    {"image": "file://书本页.jpg"},
                    {"text": "请提取图中的所有文字。要求：\n"
                             "1. 正文部分用Markdown\n"
                             "2. 公式用LaTeX（$$包裹）\n"
                             "3. 表格用Markdown表格\n"
                             "4. 分节标注【实验目的】【实验原理】等"}
                ]
            }]
        }
    }
)
```

| 项目 | 说明 |
|------|------|
| SDK | `pip install dashscope` |
| 价格 | ¥0.003/千token，约 ¥0.005/页 |
| 开通 | [阿里云百炼平台](https://bailian.console.aliyun.com) → 开通通义千问VL → 获取API Key |

### 🔧 第二阶段：专项增强（1-2天）

**接入 MathPix** — 公式精度从 95% → 99%

```python
# 公式区域专用识别
import requests
r = requests.post("https://api.mathpix.com/v3/text",
    headers={"app_id": APP_ID, "app_key": APP_KEY},
    json={"src": "https://your-image-url", "formats": ["latex"]})
latex = r.json()["text"]
```

| 项目 | 说明 |
|------|------|
| 价格 | $25/月 (1000次) 或 按次 $0.02 |
| 开通 | [mathpix.com](https://mathpix.com) → 注册 → 获取 API Key |

### 🏗️ 第三阶段：本地离线（2-3天）

**部署 PaddleOCR** — 正文/表格免费不受限

```bash
pip install paddlepaddle paddleocr
```

```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch')
result = ocr.ocr('书本页.jpg')
# PP-Structure 做表格提取
from paddleocr import PPStructure
engine = PPStructure(table=True)
result = engine('表格区域.jpg')
```

| 项目 | 说明 |
|------|------|
| 硬件 | 建议 NVIDIA GPU（CPU也可，较慢） |
| 精度 | 中文 97%+，表格 90%+ |
| 公式 | 不能直接转LaTeX，需 MathPix 补充 |

---

## 五、最终推荐

```
🥇 通义千问VL 端到端（快速原型 → 直接可用）
    ↓ 公式精度不够？
🥈 + MathPix 公式专项
    ↓ 量大想省钱？
🥉 + PaddleOCR 本地（正文+表格免费）
```

**成本汇总（100页/月）**：

| 阶段 | 工具组合 | 月成本 |
|------|---------|:--:|
| 第一阶段 | 纯通义千问VL | ~¥0.5 |
| 第二阶段 | 千问VL + MathPix | ~¥17 |
| 第三阶段 | PaddleOCR + MathPix + 千问校验 | ~¥16 |

---

## 六、集成到现有工作流

新 workflow：

```
用户拍照（书本页）
    ↓
三层识别流水线（自动）
    ↓
结构化输出：
  【实验目的】精炼文本
  【实验原理】原文 + LaTeX公式
  【实验仪器】列表
  【实验步骤】编号
    ↓
用户确认（仅审核，无需手动输入）
    ↓
AI 重写实验原理 → 填充模板 → 生成 .docx
```

### 需开发的脚本

```
.github/skills/phys-ocr/
├── SKILL.md                   ← 图像识别 Skill
└── scripts/
    ├── preprocess.py          ← OpenCV 预处理
    ├── ocr_qwen.py            ← 通义千问VL 调用
    ├── ocr_mathpix.py         ← MathPix 调用
    ├── ocr_paddle.py          ← PaddleOCR 调用
    └── pipeline.py            ← 流水线主脚本
```

---

> **建议**：先用通义千问VL试跑第一阶段（2小时），验证效果后再决定是否需要 MathPix 和 PaddleOCR。国产模型在中文场景下进步极快，端到端方案可能已经够用。
