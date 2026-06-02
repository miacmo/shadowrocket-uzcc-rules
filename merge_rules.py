from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import re

# 基于 Johnshall 的 lazy_group.conf。
# 只增强 [Proxy Group] 中的 AI 分组：
# 1. 新增 优先节点；
# 2. 新增 其他节点；
# 3. AI 默认选择 优先节点；
# 4. 保留上游 AI 分组原有选项；
# 5. 不改 [Rule] 主体，不改微信、DNS、fake-ip、IPv6。
UPSTREAM_URL = "https://raw.githubusercontent.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/refs/heads/release/lazy_group.conf"

OUTPUT_FILE = Path("sr_lazy_group_ai.conf")
UPDATE_URL = "https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_lazy_group_ai.conf"

# 排除订阅信息节点和上游区域策略组本身。
EXCLUDE_META_WORDS = (
    "剩余|流量|到期|套餐|Expire|Traffic|官网|订阅|Subscription|"
    "香港节点|台湾节点|台灣节点|日本节点|新加坡节点|韩国节点|韓國节点|美国节点|美國节点"
)

# 已归类地区关键词。其他节点必须排除这些真实节点关键词。
# 注意：韩国真实节点之前会漏进“其他节点”，所以这里补入 KR / Korea / 韩国 / 韓 / 首尔 / 春川等。
REGION_WORDS = (
    "台湾|台灣|TW|TWN|Taiwan|Taipei|taiwan|台北|台中|新北|彰化|🇹🇼|"
    "香港|HK|Hong Kong|Hong|hong|深港|沪港|京港|港|🇭🇰|"
    "新加坡|狮城|SG|Sing|Singapore|sing|沪新|京新|深新|杭新|广新|🇸🇬|"
    "日本|JP|Japan|japan|Tokyo|tokyo|东京|大阪|京日|苏日|沪日|上日|川日|深日|广日|日|🇯🇵|"
    "韩国|韓國|KR|Korea|korea|KOR|首尔|首爾|韩|韓|春川|🇰🇷|"
    "美国|美國|US|USA|America|america|United States|凤凰城|洛杉矶|洛杉磯|西雅图|西雅圖|芝加哥|纽约|紐約|沪美|美|🇺🇸"
)

PRIORITY_NODE_GROUP = (
    "优先节点 = select,"
    "policy-regex-filter=^(?=.*(台湾-|台灣-|TW-|Taiwan-|🇹🇼-))"
    f"(?!.*({EXCLUDE_META_WORDS})).*$"
)

OTHER_NODE_GROUP = (
    "其他节点 = select,"
    f"policy-regex-filter=^(?!.*({REGION_WORDS}|{EXCLUDE_META_WORDS})).*$"
)


def fetch_upstream(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 Shadowrocket-Rule-Merger"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def get_section(config: str, section_name: str) -> tuple[str, str, str]:
    pattern = re.compile(rf"(?m)^{re.escape(section_name)}\s*$")
    match = pattern.search(config)
    if not match:
        raise ValueError(f"Missing {section_name} section.")

    next_match = re.search(r"(?m)^\[[^\]]+\]\s*$", config[match.end():])
    if next_match:
        end = match.end() + next_match.start()
    else:
        end = len(config)

    return config[:match.start()], config[match.start():end], config[end:]


def join_sections(before: str, section_lines: list[str], after: str) -> str:
    section = "\n".join(section_lines).rstrip() + "\n"
    if after and not after.startswith("\n"):
        after = "\n" + after
    return before + section + after.lstrip("\n")


def upsert_general_key(config: str, key: str, value: str) -> str:
    before, section, after = get_section(config, "[General]")
    lines = section.splitlines()
    output = []
    found = False

    for line in lines:
        if re.match(rf"^\s*{re.escape(key)}\s*=", line, flags=re.IGNORECASE):
            output.append(f"{key} = {value}")
            found = True
        else:
            output.append(line)

    if not found:
        output.append(f"{key} = {value}")

    return join_sections(before, output, after)


def rebuild_ai_entry(line: str) -> str:
    """
    保留上游 AI = select,... 的原有选项，只插入 优先节点 和 其他节点。
    修正：
    - 上游 AI 里通常带 policy-select-name=PROXY，必须改成 policy-select-name=优先节点；
    - 其他节点 放在所有策略项之后、参数项之前。
    """
    _, _, value = line.partition("=")
    raw_parts = [item.strip() for item in value.split(",") if item.strip()]

    if not raw_parts:
        return "AI = select,优先节点,PROXY,DIRECT,其他节点,policy-select-name=优先节点"

    group_type = raw_parts[0]
    raw_items = raw_parts[1:]

    policy_items = []
    params = []

    for item in raw_items:
        if item.startswith("policy-select-name="):
            continue
        if "=" in item:
            params.append(item)
        else:
            policy_items.append(item)

    policy_items = [
        item for item in policy_items
        if item not in {"AI-优先", "AI-其他", "优先节点", "其他节点"}
    ]

    new_policy_items = ["优先节点"] + policy_items + ["其他节点"]
    new_params = ["policy-select-name=优先节点"] + params

    return "AI = " + ",".join([group_type] + new_policy_items + new_params)


def enhance_ai_group(config: str) -> str:
    before, section, after = get_section(config, "[Proxy Group]")
    lines = section.splitlines()
    output = []
    replaced_ai = False

    for line in lines:
        stripped = line.strip()

        # 删除脚本旧版本插入的分组，避免重复。
        if re.match(r"^AI-优先\s*=", stripped):
            continue
        if re.match(r"^AI-其他\s*=", stripped):
            continue
        if re.match(r"^优先节点\s*=", stripped):
            continue
        if re.match(r"^其他节点\s*=", stripped):
            continue

        if re.match(r"^AI\s*=", stripped):
            output.append(rebuild_ai_entry(stripped))
            replaced_ai = True
            continue

        # 在香港节点定义前放入“优先节点”的定义。
        if re.match(r"^香港节点\s*=", stripped):
            output.append("")
            output.append("# 优先节点：只收录标准台湾前缀节点")
            output.append(PRIORITY_NODE_GROUP)
            output.append("")
            output.append(line)
            continue

        output.append(line)

    if not replaced_ai:
        raise ValueError("Missing AI entry in [Proxy Group]. Upstream lazy_group.conf may have changed.")

    # 兜底：如果上游没有香港节点定义，就把优先节点放在 [Proxy Group] 底部的其他节点上方。
    if not any(re.match(r"^优先节点\s*=", line.strip()) for line in output):
        output.append("")
        output.append("# 优先节点：只收录标准台湾前缀节点")
        output.append(PRIORITY_NODE_GROUP)

    # 把“其他节点”放到 [Proxy Group] 最下面。
    output.append("")
    output.append("# 其他节点：排除已归类地区、韩国节点、上游区域策略组和订阅信息节点")
    output.append(OTHER_NODE_GROUP)

    return join_sections(before, output, after)


def main() -> None:
    upstream = fetch_upstream(UPSTREAM_URL)

    # 只改 update-url，避免 Shadowrocket 更新时跳回 Johnshall 原始地址。
    # 不改 DNS / fake-ip / IPv6 / 微信 / [Rule] 主体。
    upstream = upsert_general_key(upstream, "update-url", UPDATE_URL)

    merged = enhance_ai_group(upstream)

    generated_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    banner = (
        f"# ============================================================\n"
        f"# 自动生成的配置文件\n"
        f"# 生成时间：{generated_time}\n"
        f"# 上游规则：{UPSTREAM_URL}\n"
        f"# 输出文件：{OUTPUT_FILE}\n"
        f"# 修改范围：仅增强 [Proxy Group] 的 AI 分组\n"
        f"# ============================================================\n\n"
    )

    OUTPUT_FILE.write_text(banner + merged, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
