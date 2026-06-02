from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

# 使用 Johnshall 的 lazy.conf 作为底座。
UPSTREAM_URL = "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/lazy.conf"

CUSTOM_RULES_FILE = Path("uzcc_rules.txt")
OUTPUT_FILE = Path("sr_lazy_ai_routing.conf")


CUSTOM_PROXY_GROUP = """
[Proxy Group]

# AI 分流入口，优先使用命名为“台湾-”的节点，其余地区可手动选择
AI = select,AI-优先,AI-台湾,AI-香港,AI-新加坡,AI-日本,AI-美国,AI-其他,PROXY,DIRECT

# 优先入口：只收录“台湾- / 台灣- / TW- / Taiwan- / 🇹🇼-”这类标准前缀节点
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


def upsert_general_key(config: str, key: str, value: str) -> str:
    """
    只在 [General] 段内更新或插入指定键。
    """
    lines = config.splitlines()
    out = []
    in_general = False
    found = False

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        if stripped.startswith("[") and stripped.endswith("]"):
            if in_general and not found:
                out.append(f"{key} = {value}")
                found = True
            in_general = lower == "[general]"

        if in_general and lower.startswith(f"{key.lower()}"):
            out.append(f"{key} = {value}")
            found = True
        else:
            out.append(line)

    if in_general and not found:
        out.append(f"{key} = {value}")

    return "\n".join(out) + ("\n" if config.endswith("\n") else "")


def remove_cidr_from_general_list(config: str, keys: tuple[str, ...], target: str) -> str:
    """
    从 bypass-tun / tun-excluded-routes 等列表字段里移除指定 CIDR。
    这里保留这个修正是为了避免上游变动时把 fake-ip 段重新放回 TUN 绕行列表。
    """
    out = []
    for line in config.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if any(lower.startswith(k.lower()) for k in keys) and target in line:
            key, sep, value = line.partition("=")
            if sep:
                cidrs = [
                    item.strip()
                    for item in value.split(",")
                    if item.strip() and item.strip() != target
                ]
                line = f"{key.rstrip()} = " + ", ".join(cidrs)
        out.append(line)
    return "\n".join(out) + ("\n" if config.endswith("\n") else "")


def normalize_general(upstream: str) -> str:
    """
    使用 lazy.conf 的默认 General 逻辑，不强行上 always-real-ip / dns-direct-system。
    只做两件确定需要的事：
    1. 接管 IPv6，但不优先 IPv6 回源；
    2. 防止 198.18.0.0/15 被放进 TUN 绕行列表。
    """
    upstream = upsert_general_key(upstream, "ipv6", "true")
    upstream = upsert_general_key(upstream, "prefer-ipv6", "false")

    # 不启用 dns-direct-system。默认规则能正常微信，就不要再强改 DNS 行为。
    # 如果上游已有 dns-direct-system，统一设为 false。
    upstream = upsert_general_key(upstream, "dns-direct-system", "false")

    upstream = remove_cidr_from_general_list(
        upstream,
        keys=("bypass-tun", "tun-excluded-routes"),
        target="198.18.0.0/15",
    )
    return upstream


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
# 以下为上游 lazy.conf 默认规则
# ============================================================

"""

    return before_rule.rstrip() + "\n\n" + header + custom_block + after_rule.lstrip()


def main() -> None:
    if not CUSTOM_RULES_FILE.exists():
        raise FileNotFoundError(f"Custom rules file not found: {CUSTOM_RULES_FILE}")

    upstream = fetch_upstream(UPSTREAM_URL)
    upstream = normalize_general(upstream)

    custom_rules = CUSTOM_RULES_FILE.read_text(encoding="utf-8")

    upstream_with_group = insert_proxy_group(upstream)
    merged = insert_custom_rules(upstream_with_group, custom_rules)

    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
