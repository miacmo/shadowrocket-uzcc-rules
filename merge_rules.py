from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

UPSTREAM_URL = "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf"

OVERSEAS_AI_URL = (
    "https://raw.githubusercontent.com/viewer12/OverseasAI.list/"
    "main/rule/Shadowrocket/OverseasAI/OverseasAI.list"
)

CUSTOM_RULES_FILE = Path("uzcc_rules.txt")
AI_RULE_SET_FILE = Path("ai_rule_set.list")
OUTPUT_FILE = Path("sr_cnip_ai_routing.conf")


CUSTOM_PROXY_GROUP = """
[Proxy Group]

# AI 分流入口，具体出口在下面几个地区分组里选
AI = select,AI-台湾,AI-香港,AI-新加坡,AI-日本,AI-美国,AI-其他,PROXY,DIRECT

# 按节点名称自动归类，排除订阅信息类节点
AI-台湾 = select,policy-regex-filter=^(?=.*(台湾|台灣|TW|Taiwan|🇹🇼))(?!.*(剩余|流量|到期|套餐)).*$
AI-香港 = select,policy-regex-filter=^(?=.*(香港|HK|Hong Kong|🇭🇰))(?!.*(剩余|流量|到期|套餐)).*$
AI-新加坡 = select,policy-regex-filter=^(?=.*(新加坡|狮城|SG|Singapore|🇸🇬))(?!.*(剩余|流量|到期|套餐)).*$
AI-日本 = select,policy-regex-filter=^(?=.*(日本|JP|Japan|🇯🇵))(?!.*(剩余|流量|到期|套餐)).*$
AI-美国 = select,policy-regex-filter=^(?=.*(美国|美國|US|USA|United States|America|🇺🇸))(?!.*(剩余|流量|到期|套餐)).*$
AI-其他 = select,policy-regex-filter=^(?!.*(台湾|台灣|TW|Taiwan|🇹🇼|香港|HK|Hong Kong|🇭🇰|新加坡|狮城|SG|Singapore|🇸🇬|日本|JP|Japan|🇯🇵|美国|美國|US|USA|United States|America|🇺🇸|剩余|流量|到期|套餐)).*$
"""


# 只从上游 AI 规则集中提取这些服务
ALLOW_KEYWORDS = [
    # OpenAI / ChatGPT / Sora
    "openai",
    "chatgpt",
    "oaistatic",
    "oaiusercontent",
    "sora",

    # Claude / Anthropic
    "anthropic",
    "claude",

    # Perplexity
    "perplexity",
    "pplx",

    # Poe
    "poe",
    "poecdn",

    # xAI / Grok / Groq
    "x.ai",
    "grok",
    "groq",

    # Mistral
    "mistral",

    # Character AI
    "character.ai",
    "characterai",

    # Midjourney
    "midjourney",

    # Stability / DreamStudio
    "stability",
    "dreamstudio",

    # Runway
    "runwayml",

    # Pika
    "pika.art",

    # Suno
    "suno",

    # ElevenLabs
    "elevenlabs",

    # Cursor
    "cursor",

    # Replit
    "replit",

    # Hugging Face
    "huggingface",
    "hf.co",

    # Replicate
    "replicate",

    # Cohere
    "cohere",

    # Together
    "together",

    # Fireworks / OpenRouter
    "fireworks",
    "openrouter",

    # 搜索与开发类工具
    "phind",
    "devv",
    "forefront",

    # 演示与文档类工具
    "gamma.app",
    "tome.app",

    # Notion
    "notion",
]


# 即使命中白名单，也强制排除这些内容
DENY_KEYWORDS = [
    # Google / Gemini
    "google",
    "googleapis",
    "googleusercontent",
    "gstatic",
    "gemini",
    "aistudio",
    "makersuite",
    "generativelanguage",
    "notebooklm",

    # Microsoft / Copilot / Bing
    "microsoft",
    "windows",
    "office",
    "live.com",
    "msn.com",
    "copilot",
    "bing",
    "bingapis",

    # Canva
    "canva",

    # 中国 AI / 国内大模型
    "deepseek",
    "kimi",
    "moonshot",
    "doubao",
    "volcengine",
    "byteplus",
    "bytedance",
    "qwen",
    "tongyi",
    "aliyun",
    "alibaba",
    "dashscope",
    "baidu",
    "ernie",
    "wenxin",
    "yiyan",
    "zhipu",
    "bigmodel",
    "chatglm",
    "minimax",
    "abab",
    "hunyuan",
    "tencent",
    "yuanbao",
    "baichuan",
    "01.ai",
    "lingyiwanwu",
    "stepfun",
    "siliconflow",
    "sensenova",
    "sensecore",
]


def fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 Shadowrocket-Rule-Merger"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def should_keep_rule(line: str) -> bool:
    text = line.strip().lower()

    if not text:
        return False

    if text.startswith("#"):
        return False

    if any(keyword.lower() in text for keyword in DENY_KEYWORDS):
        return False

    return any(keyword.lower() in text for keyword in ALLOW_KEYWORDS)


def build_ai_rule_set() -> None:
    source = fetch_text(OVERSEAS_AI_URL)
    generated_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    output_lines = [
        "# ============================================================",
        "# AI rule set",
        f"# Generated at: {generated_time}",
        f"# Source: {OVERSEAS_AI_URL}",
        "# Mode: whitelist extraction",
        "# Included: selected overseas AI services",
        "# Excluded: Google / Gemini / Microsoft / Copilot / Bing / Canva / China AI",
        "# ============================================================",
        "",
    ]

    seen = set()

    for raw_line in source.splitlines():
        line = raw_line.strip()

        if not should_keep_rule(line):
            continue

        if line in seen:
            continue

        seen.add(line)
        output_lines.append(line)

    AI_RULE_SET_FILE.write_text("\n".join(output_lines) + "\n", encoding="utf-8")


def insert_proxy_group(upstream: str) -> str:
    marker = "[Rule]"
    if marker not in upstream:
        raise ValueError("Missing [Rule] section in upstream configuration.")

    before_rule, after_rule = upstream.split(marker, 1)

    return (
        before_rule.rstrip()
        + "\n\n"
        + CUSTOM_PROXY_GROUP.strip()
        + "\n\n[Rule]"
        + after_rule
    )


def insert_custom_rules(upstream: str, custom_rules: str) -> str:
    marker = "[Rule]"
    if marker not in upstream:
        raise ValueError("Missing [Rule] section in upstream configuration.")

    before_rule, after_rule = upstream.split(marker, 1)
    generated_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    header = f"""
# ============================================================
# 自动生成的配置文件
# 生成时间：{generated_time}
# 上游规则：{UPSTREAM_URL}
# AI 规则源：{OVERSEAS_AI_URL}
# 自定义规则：{CUSTOM_RULES_FILE}
# AI 规则集：{AI_RULE_SET_FILE}
# 输出文件：{OUTPUT_FILE}
# ============================================================

"""

    custom_block = f"""
[Rule]

# ============================================================
# 自定义规则开始
# ============================================================

{custom_rules.strip()}

# ============================================================
# 自定义规则结束
# 以下为上游规则
# ============================================================

"""

    return before_rule.rstrip() + "\n\n" + header + custom_block + after_rule.lstrip()


def main() -> None:
    if not CUSTOM_RULES_FILE.exists():
        raise FileNotFoundError(f"Custom rules file not found: {CUSTOM_RULES_FILE}")

    build_ai_rule_set()

    upstream = fetch_text(UPSTREAM_URL)
    custom_rules = CUSTOM_RULES_FILE.read_text(encoding="utf-8")

    upstream_with_group = insert_proxy_group(upstream)
    merged = insert_custom_rules(upstream_with_group, custom_rules)

    OUTPUT_FILE.write_text(merged, encoding="utf-8")

    print(f"Generated {AI_RULE_SET_FILE}")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
