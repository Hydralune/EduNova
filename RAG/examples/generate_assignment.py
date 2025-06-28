import os, json, yaml, pathlib
from openai import OpenAI            # 远程模式；本地 Ollama 见下文
import string
PROMPT_FILE = pathlib.Path(__file__).parent.parent / "prompts" / "zh.yaml"

# 1) 载入 YAML 提示词仓库
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)

def render_prompt(p_type, **vars):
    tpl = prompts[p_type]
    return string.Template(tpl).substitute(vars)

# ─── 示例参数 ──────────────────────────────────────────────
course_name = "计算机网络"
context = """
1. 网络分层思想
2. 物理层常用编码：NRZ、曼彻斯特
3. 数据链路层差错控制：CRC
4. 网络层 IP 分片与重组
"""

# 2) 渲染提示词
prompt = render_prompt("assignment", course_name=course_name, context=context)

# 3) 调用 LLM（SiliconFlow OpenAI 兼容接口）
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_API_BASE"),
)

response = client.chat.completions.create(
    model=os.getenv("LLM_MODEL"),           # 例如 deepseek-ai/DeepSeek-V3
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"} # 要求返回 JSON
)

json_text = response.choices[0].message.content
data = json.loads(json_text)

# 4) 保存并打印
out_path = pathlib.Path("assignment_demo.json")
out_path.write_text(json_text, encoding="utf-8")
print("生成完毕，已写入", out_path)
print(json.dumps(data, indent=2, ensure_ascii=False))