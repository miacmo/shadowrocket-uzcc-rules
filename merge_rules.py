from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

UPSTREAM_URL = "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf"

CUSTOM_RULES_FILE = Path("uzcc_rules.txt")
OUTPUT_FILE = Path("sr_cnip_ai_routing.conf")


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


WECHAT_ALWAYS_REAL_IP = [
    "*.qq.com",
    "*.weixin.qq.com",
    "*.weixin.com",
    "*.wechat.com",
    "*.wechatpay.com",
    "*.wechatlegal.net",
    "*.wechatos.net",
    "*.weixinbridge.com",
    "*.weixinsxy.com",
    "*.servicewechat.com",
    "*.qpic.cn",
    "*.qlogo.cn",
    "*.gtimg.com",
    "*.gtimg.cn",
    "*.idqqimg.com",
    "*.wx.gtimg.com",
    "*.wx.qq.com",
    "*.wxs.qq.com",
    "*.wxapp.tc.qq.com",
    "*.vweixinthumb.tc.qq.com",
    "*.map.qq.com",
    "*.iot-tencent.com",
    "*.tenpay.com",
    "*.wechatpay.cn",
    "*.up-hl.3g.qq.com",
    "*.yun-hl.3g.qq.com",
    "mp.weixin.qq.com",
    "res.wx.qq.com",
    "mmbiz.qpic.cn",
    "mmbiz.qlogo.cn",
    "weixin110.qq.com",
    "vweixinf.tc.qq.com",
    "btrace.qq.com",
    "dldir1.qq.com",
    "wup.imtt.qq.com",
    "apd-pcdnwxlogin.teg.tencent-cloud.net",
]


def ensure_always_real_ip(config: str) -> str:
    """
    给微信/腾讯资源域名启用 always-real-ip，让这些域名返回真实 IP，
    避免 fake-ip 在微信图片、头像、小程序 CDN 场景下触发白图问题。

    注意：这里只做微信/腾讯资源的局部修复，不全局关闭 fake-ip，
    不改变 AI、PROXY、DNS、IPv6 的既有逻辑。
    """
    key_name = "always-real-ip"
    wanted = WECHAT_ALWAYS_REAL_IP

    out = []
    found = False

    for line in config.splitlines():
        stripped = line.strip().lower()
        if stripped.startswith(f"{key_name}"):
            key, sep, value = line.partition("=")
            if sep:
                existing = [item.strip() for item in value.split(",") if item.strip()]
                merged = existing[:]
                for item in wanted:
                    if item not in merged:
                        merged.append(item)
                line = f"{key.rstrip()} = " + ", ".join(merged)
                found = True
        out.append(line)

    if not found:
        new_out = []
        inserted = False
        for line in out:
            new_out.append(line)
            if line.strip().lower().startswith("dns-server"):
                new_out.append(f"{key_name} = " + ", ".join(wanted))
                inserted = True

        if not inserted:
            # 兜底插入到 [General] 内部，避免追加到文件末尾导致 section 错位。
            general_index = None
            for index, line in enumerate(new_out):
                if line.strip() == "[General]":
                    general_index = index
                    break
            if general_index is None:
                raise ValueError("Missing [General] section in upstream configuration.")
            new_out.insert(general_index + 1, f"{key_name} = " + ", ".join(wanted))

        out = new_out

    return "\n".join(out) + ("\n" if config.endswith("\n") else "")


def enforce_ipv6_policy(config: str) -> str:
    """
    强制启用 IPv6 TUN 接管，但不优先使用 IPv6 回源。

    上游默认 ipv6=false 会让公网 IPv6 可能绕过 TUN；这里固定改成
    ipv6=true，并确保 prefer-ipv6=false，符合本项目“管住 IPv6，
    但实际优先 IPv4”的设计。
    """
    out = []
    in_general = False
    found_ipv6 = False
    found_prefer_ipv6 = False

    for line in config.splitlines():
        stripped = line.strip()
        lower = stripped.lower()

        if stripped == "[General]":
            in_general = True
            out.append(line)
            continue

        if stripped.startswith("[") and stripped.endswith("]") and stripped != "[General]":
            if in_general:
                if not found_ipv6:
                    out.append("ipv6 = true")
                    found_ipv6 = True
                if not found_prefer_ipv6:
                    out.append("prefer-ipv6 = false")
                    found_prefer_ipv6 = True
            in_general = False
            out.append(line)
            continue

        if in_general and lower.startswith("ipv6"):
            out.append("ipv6 = true")
            found_ipv6 = True
            continue

        if in_general and lower.startswith("prefer-ipv6"):
            out.append("prefer-ipv6 = false")
            found_prefer_ipv6 = True
            continue

        out.append(line)

    if in_general:
        if not found_ipv6:
            out.append("ipv6 = true")
        if not found_prefer_ipv6:
            out.append("prefer-ipv6 = false")

    return "\n".join(out) + ("\n" if config.endswith("\n") else "")


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
    upstream = enforce_ipv6_policy(upstream)
    upstream = strip_fakeip_from_bypass_tun(upstream)
    upstream = ensure_always_real_ip(upstream)

    custom_rules = CUSTOM_RULES_FILE.read_text(encoding="utf-8")

    upstream_with_group = insert_proxy_group(upstream)
    merged = insert_custom_rules(upstream_with_group, custom_rules)

    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
