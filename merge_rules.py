from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import re

# 直接基于 Johnshall 的 lazy_group.conf。
# 只增强 AI 分组：新增 AI-优先、AI-其他，并把它们合入 AI 入口。
# 不重构上游规则，不改微信、DNS、fake-ip、IPv6 等主体逻辑。
UPSTREAM_URL = "https://raw.githubusercontent.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/refs/heads/release/lazy_group.conf"

CUSTOM_RULES_FILE = Path("uzcc_rules.txt")
OUTPUT_FILE = Path("sr_lazy_group_ai.conf")

EXCLUDE_WORDS = (
    "剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription|"
    "香港节点|台湾节点|台灣节点|日本节点|新加坡节点|韩国节点|韓國节点|美国节点|美國节点"
)

AI_PRIORITY_GROUP = (
    "AI-优先 = select,"
    "policy-regex-filter=^(?=.*(台湾-|台灣-|TW-|Taiwan-|🇹🇼-))"
    f"(?!.*({EXCLUDE_WORDS})).*$"
)

AI_OTHER_GROUP = (
    "AI-其他 = select,"
    "policy-regex-filter=^(?!.*("
    "台湾|台灣|TW|Taiwan|🇹🇼|"
    "香港|HK|Hong Kong|🇭🇰|"
    "新加坡|狮城|SG|Singapore|🇸🇬|"
    "日本|JP|Japan|🇯🇵|"
    "美国|美國|US|USA|United States|America|🇺🇸|"
    f"{EXCLUDE_WORDS}"
    ")).*$"
)

AI_ENTRY = "AI = select,AI-优先,AI-台湾,AI-香港,AI-新加坡,AI-日本,AI-美国,AI-其他,PROXY,DIRECT"


def fetch_upstream(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 Shadowrocket-Rule-Merger"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def split_sections(config: str, section_name: str) -> tuple[str, str, str]:
    """
    返回 section 前、section 内容、section 后。
    section_name 例：[Proxy Group]
    """
    start = config.find(section_name)
    if start == -1:
        raise ValueError(f"Missing {section_name} section.")

    next_section = re.search(r"\n\[[^\]]+\]", config[start + len(section_name):])
    if next_section:
        end = start + len(section_name) + next_section.start()
    else:
        end = len(config)

    return config[:start], config[start:end], config[end:]


def enhance_ai_proxy_group(config: str) -> str:
    """
    只处理 [Proxy Group] 中的 AI 相关分组：
    1. 把 AI 入口替换为包含 AI-优先 和 AI-其他的新入口；
    2. 删除旧的 AI-优先 / AI-其他，避免重复；
    3. 在 AI 入口后插入新的 AI-优先 / AI-其他；
    4. 不重写上游已有的 AI-台湾 / AI-香港 / AI-新加坡 / AI-日本 / AI-美国。
    """
    before, section, after = split_sections(config, "[Proxy Group]")
    lines = section.splitlines()

    new_lines = []
    inserted_extra_groups = False
    found_ai_entry = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("AI-优先"):
            continue
        if stripped.startswith("AI-其他"):
            continue

        if stripped.startswith("AI ="):
            new_lines.append(AI_ENTRY)
            new_lines.append("")
            new_lines.append("# AI 优先入口：只收录标准台湾前缀节点")
            new_lines.append(AI_PRIORITY_GROUP)
            new_lines.append("")
            new_lines.append("# AI 其他入口：排除已归类地区、上游区域策略组和订阅信息节点")
            new_lines.append(AI_OTHER_GROUP)
            inserted_extra_groups = True
            found_ai_entry = True
            continue

        new_lines.append(line)

    if not found_ai_entry:
        raise ValueError("Missing AI entry in [Proxy Group].")

    if not inserted_extra_groups:
        raise RuntimeError("Failed to insert AI extra groups.")

    return before + "\n".join(new_lines) + after


def insert_custom_rules(config: str, custom_rules: str) -> str:
    """
    把自定义规则插入 [Rule] 顶部，优先于上游规则。
    这里主要放 Bing/Copilot 直连、AI 规则、ChinaMax。
    """
    marker = "[Rule]"
    if marker not in config:
        raise ValueError("Missing [Rule] section.")

    before_rule, after_rule = config.split(marker, 1)

    generated_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    header = f"""
# ============================================================
# 自动生成的配置文件
# 生成时间：{generated_time}
# 上游规则：{UPSTREAM_URL}
# 自定义规则：{CUSTOM_RULES_FILE}
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
# 以下为上游 lazy_group.conf 默认规则
# ============================================================

"""

    return before_rule.rstrip() + "\n\n" + header + custom_block + after_rule.lstrip()


def main() -> None:
    if not CUSTOM_RULES_FILE.exists():
        raise FileNotFoundError(f"Custom rules file not found: {CUSTOM_RULES_FILE}")

    upstream = fetch_upstream(UPSTREAM_URL)

    # 只增强 AI 策略组，不碰上游 General / Rule 主体逻辑。
    enhanced = enhance_ai_proxy_group(upstream)

    custom_rules = CUSTOM_RULES_FILE.read_text(encoding="utf-8")
    merged = insert_custom_rules(enhanced, custom_rules)

    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
