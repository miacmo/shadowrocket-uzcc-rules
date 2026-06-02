from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

UPSTREAM_URL = "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf"

CUSTOM_RULES_FILE = Path("uzcc_rules.txt")
OUTPUT_FILE = Path("sr_cnip_ai_routing.conf")

DEFAULT_IPV6_COMMENT = "# 启用 IPv6 接管，避免公网 IPv6 绕过 TUN；实际连接通过 prefer-ipv6=false 优先 IPv4"
LEGACY_IPV6_COMMENTS = {
    "# 默认关闭 ipv6 支持，如果需要请手动开启",
}


CUSTOM_PROXY_GROUP = """
[Proxy Group]

# AI 分流入口，优先使用命名为“台湾-”的节点，其余地区可手动选择
AI = select,AI-优先,AI-台湾,AI-香港,AI-新加坡,AI-日本,AI-美国,AI-其他,PROXY,DIRECT

# 优先入口：只收录“台湾-”这类节点
AI-优先 = select,policy-regex-filter=^(?=.*(台湾-|台灣-|TW-|Taiwan-|🇹🇼-))(?!.*(剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription)).*$

# 地区入口：按节点名称自动归类，排除订阅信息类节点
AI-台湾 = select,policy-regex-filter=^(?=.*(台湾|台灣|TW|Taiwan|🇹🇼))(?!.*(剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription)).*$
AI-香港 = select,policy-regex-filter=^(?=.*(香港|HK|Hong Kong|🇭🇰))(?!.*(剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription)).*$
AI-新加坡 = select,policy-regex-filter=^(?=.*(新加坡|狮城|SG|Singapore|🇸🇬))(?!.*(剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription)).*$
AI-日本 = select,policy-regex-filter=^(?=.*(日本|JP|Japan|🇯🇵))(?!.*(剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription)).*$
AI-美国 = select,policy-regex-filter=^(?=.*(美国|美國|US|USA|United States|America|🇺🇸))(?!.*(剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription)).*$

# 其他未命中上述地区关键词的节点
AI-其他 = select,policy-regex-filter=^(?!.*(台湾|台灣|TW|Taiwan|🇹🇼|香港|HK|Hong Kong|🇭🇰|新加坡|狮城|SG|Singapore|🇸🇬|日本|JP|Japan|🇯🇵|美国|美國|US|USA|United States|America|🇺🇸|剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription)).*$
"""


def fetch_upstream(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 Shadowrocket-Rule-Merger"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def normalize_ipv6_settings(config: str) -> str:
    """
    Normalize IPv6-related settings in the [General] section.

    Behavior:
    1. Remove existing prefer-ipv4 and prefer-ipv6 preference lines.
    2. Force `ipv6 = true` so Shadowrocket takes over IPv6 traffic instead of
       letting public IPv6 bypass the TUN through the system's native network.
    3. Insert `prefer-ipv6 = false` right after `ipv6 = true` so dual-stack
       domains prefer IPv4 when Shadowrocket performs resolution or connection
       selection.
    4. If the upstream [General] section has no `ipv6 = ...` line, insert both
       `ipv6 = true` and `prefer-ipv6 = false` near the end of [General].

    This does not block IPv6 globally. It keeps IPv6 under Shadowrocket control
    while avoiding IPv6-first connection behavior.
    """
    lines = []
    for line in config.splitlines():
        stripped_original = line.strip()
        stripped = stripped_original.lower()
        if stripped_original in LEGACY_IPV6_COMMENTS:
            line = DEFAULT_IPV6_COMMENT
        if stripped in {"prefer-ipv4 = true", "prefer-ipv4 = false", "prefer-ipv6 = true", "prefer-ipv6 = false"}:
            continue
        lines.append(line)

    general_index = None
    for index, line in enumerate(lines):
        if line.strip() == "[General]":
            general_index = index
            break

    if general_index is None:
        raise ValueError("Missing [General] section in upstream configuration.")

    insert_index = general_index + 1

    for index in range(general_index + 1, len(lines)):
        stripped = lines[index].strip().lower()

        if stripped.startswith("[") and stripped.endswith("]"):
            break

        insert_index = index + 1

        if stripped in {"ipv6 = true", "ipv6 = false"}:
            lines[index] = "ipv6 = true"
            lines.insert(index + 1, "prefer-ipv6 = false")
            return "\n".join(lines) + "\n"

    lines.insert(insert_index, DEFAULT_IPV6_COMMENT)
    lines.insert(insert_index + 1, "ipv6 = true")
    lines.insert(insert_index + 2, "prefer-ipv6 = false")
    return "\n".join(lines) + "\n"


def normalize_direct_dns_settings(config: str) -> str:
    """
    Force DIRECT-domain DNS resolution to use the system DNS.

    This improves compatibility for domestic DIRECT traffic and CDN-heavy apps
    such as WeChat. Without this, DIRECT domains can still be handled through
    Shadowrocket's fake-ip/TUN DNS path, which may break some domestic image,
    avatar, sticker, payment, or mini-program resources even when the rule
    itself correctly matches DIRECT.

    This only affects domains that match DIRECT policies. AI and other proxy
    traffic still follows their proxy policy and is not changed to DIRECT.
    """
    lines = config.splitlines()

    general_index = None
    for index, line in enumerate(lines):
        if line.strip() == "[General]":
            general_index = index
            break

    if general_index is None:
        raise ValueError("Missing [General] section in upstream configuration.")

    insert_index = general_index + 1
    for index in range(general_index + 1, len(lines)):
        stripped = lines[index].strip().lower()
        if stripped.startswith("[") and stripped.endswith("]"):
            break

        insert_index = index + 1
        if stripped.startswith("dns-direct-system"):
            lines[index] = "dns-direct-system = true"
            return "\n".join(lines) + ("\n" if config.endswith("\n") else "")

    lines.insert(insert_index, "dns-direct-system = true")
    return "\n".join(lines) + ("\n" if config.endswith("\n") else "")


def strip_fakeip_from_bypass_tun(config: str) -> str:
    """
    Remove the fake-ip range (198.18.0.0/15) from the upstream `bypass-tun`
    line. Shadowrocket hands out fake IPs inside 198.18.x.x, and fake-ip ONLY
    works if that range is routed THROUGH the TUN. Leaving 198.18.0.0/15 in
    bypass-tun tells the OS to bypass the TUN for exactly those addresses, which
    breaks SR's fake-ip -> real-host relay for some destinations (e.g. Tencent).
    """
    target = "198.18.0.0/15"
    out = []
    for line in config.splitlines():
        if line.strip().lower().startswith("bypass-tun") and target in line:
            key, _, value = line.partition("=")
            cidrs = [c.strip() for c in value.split(",") if c.strip() and c.strip() != target]
            line = f"{key.rstrip()} = " + ",".join(cidrs)
        out.append(line)
    return "\n".join(out) + ("\n" if config.endswith("\n") else "")


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
    upstream = normalize_ipv6_settings(upstream)
    upstream = normalize_direct_dns_settings(upstream)
    upstream = strip_fakeip_from_bypass_tun(upstream)

    custom_rules = CUSTOM_RULES_FILE.read_text(encoding="utf-8")

    upstream_with_group = insert_proxy_group(upstream)
    merged = insert_custom_rules(upstream_with_group, custom_rules)

    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
