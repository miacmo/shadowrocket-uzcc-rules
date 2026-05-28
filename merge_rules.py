from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

UPSTREAM_URL = "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf"

CUSTOM_RULES_FILE = Path("uzcc_rules.txt")
OUTPUT_FILE = Path("sr_cnip_ai_routing.conf")


CUSTOM_PROXY_GROUP = """
[Proxy Group]

# AI 分流入口，优先使用命名为“台湾-”的节点，其余地区可手动选择
AI = select,AI-优先,AI-台湾,AI-香港,AI-新加坡,AI-日本,AI-美国,AI-其他,Proxy,DIRECT

# 优先入口：只收录“台湾-”这类节点
AI-优先 = select,policy-regex-filter=^(?=.*(台湾-|台灣-|TW-|Taiwan-|🇹🇼-))(?!.*(剩余|流量|到期|套餐)).*$

# 地区入口：按节点名称自动归类，排除订阅信息类节点
AI-台湾 = select,policy-regex-filter=^(?=.*(台湾|台灣|TW|Taiwan|🇹🇼))(?!.*(剩余|流量|到期|套餐)).*$
AI-香港 = select,policy-regex-filter=^(?=.*(香港|HK|Hong Kong|🇭🇰))(?!.*(剩余|流量|到期|套餐)).*$
AI-新加坡 = select,policy-regex-filter=^(?=.*(新加坡|狮城|SG|Singapore|🇸🇬))(?!.*(剩余|流量|到期|套餐)).*$
AI-日本 = select,policy-regex-filter=^(?=.*(日本|JP|Japan|🇯🇵))(?!.*(剩余|流量|到期|套餐)).*$
AI-美国 = select,policy-regex-filter=^(?=.*(美国|美國|US|USA|United States|America|🇺🇸))(?!.*(剩余|流量|到期|套餐)).*$

# 其他未命中上述地区关键词的节点
AI-其他 = select,policy-regex-filter=^(?!.*(台湾|台灣|TW|Taiwan|🇹🇼|香港|HK|Hong Kong|🇭🇰|新加坡|狮城|SG|Singapore|🇸🇬|日本|JP|Japan|🇯🇵|美国|美國|US|USA|United States|America|🇺🇸|剩余|流量|到期|套餐)).*$
"""


def fetch_upstream(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 Shadowrocket-Rule-Merger"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def ensure_prefer_ipv6_false(config: str) -> str:
    """
    Remove `prefer-ipv4 = true` and ensure `prefer-ipv6 = false`
    is present in the [General] section.

    This function is idempotent. It is safe to run on every scheduled update.
    """
    lines = [
        line for line in config.splitlines()
        if line.strip().lower() != "prefer-ipv4 = true"
    ]

    if any(line.strip().lower() == "prefer-ipv6 = false" for line in lines):
        return "\n".join(lines) + "\n"

    general_index = None
    for index, line in enumerate(lines):
        if line.strip() == "[General]":
            general_index = index
            break

    if general_index is None:
        raise ValueError("Missing [General] section in upstream configuration.")

    insert_index = general_index + 1

    for index in range(general_index + 1, len(lines)):
        stripped = lines[index].strip()

        if stripped.startswith("[") and stripped.endswith("]"):
            break

        insert_index = index + 1

        if stripped.lower() == "ipv6 = true":
            lines.insert(index + 1, "prefer-ipv6 = false")
            return "\n".join(lines) + "\n"

    lines.insert(insert_index, "prefer-ipv6 = false")
    return "\n".join(lines) + "\n"


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
# 以下为上游规则
# ============================================================

"""

    return before_rule.rstrip() + "\n\n" + header + custom_block + after_rule.lstrip()


def main() -> None:
    if not CUSTOM_RULES_FILE.exists():
        raise FileNotFoundError(f"Custom rules file not found: {CUSTOM_RULES_FILE}")

    upstream = fetch_upstream(UPSTREAM_URL)
    upstream = ensure_prefer_ipv6_false(upstream)

    custom_rules = CUSTOM_RULES_FILE.read_text(encoding="utf-8")

    upstream_with_group = insert_proxy_group(upstream)
    merged = insert_custom_rules(upstream_with_group, custom_rules)

    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
