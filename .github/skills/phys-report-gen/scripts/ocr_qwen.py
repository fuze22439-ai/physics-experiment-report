"""
通义千问VL OCR — 书本页图片 → 结构化 Markdown + LaTeX
依赖：pip install openai python-dotenv Pillow
用法：python ocr_qwen.py 图片1.jpg 图片2.jpg ...
"""
import os, sys, base64, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_KEY = os.getenv('QWEN_API_KEY')
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

if not API_KEY:
    print("错误：未设置 QWEN_API_KEY，请检查 .env 文件")
    sys.exit(1)

PROMPT = """你是一位专业的OCR助手。请仔细读取图片中的所有文字内容，按以下格式输出：

1. 保持原文结构，注明标题层级（如 # 实验名称、## 实验目的 等）
2. 数学公式用 LaTeX 格式：行内公式用 $...$，独立公式用 $$...$$
3. 表格用 Markdown 表格格式
4. 图片中的插图、示意图用 [图片：描述] 标注
5. 不要添加任何原文中没有的内容，不要发挥
6. 不要加"好的"、"以下是提取结果"等客套话，直接输出内容"""


def encode_image(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def ocr_image(image_path):
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    b64 = encode_image(image_path)
    ext = os.path.splitext(image_path)[1].lower().replace('.', '')
    mime = f"image/{'jpeg' if ext in ('jpg','jpeg') else ext}"

    resp = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": PROMPT}
            ]
        }],
        temperature=0.1,
        max_tokens=4096
    )
    return resp.choices[0].message.content


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python ocr_qwen.py 图片1.jpg 图片2.jpg ...")
        sys.exit(1)

    for img in sys.argv[1:]:
        if not os.path.exists(img):
            print(f"跳过：{img} 不存在")
            continue
        print(f"\n{'='*60}")
        print(f"识别：{os.path.basename(img)}")
        print(f"{'='*60}")
        try:
            text = ocr_image(img)
            print(text)
            out = os.path.splitext(img)[0] + '_ocr.md'
            with open(out, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n✅ 已保存：{out}")
        except Exception as e:
            print(f"❌ 错误：{e}")
