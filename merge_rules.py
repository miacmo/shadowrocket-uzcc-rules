from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import re

# 基于 Johnshall 的 lazy_group.conf。
# 只增强 [Proxy Group] 中的 AI 分组：
# 1. 新增 AI-优先；
# 2. 新增 AI-其他；
# 3. 保留上游 AI 分组原有选项；
# 4. 不改 [Rule] 主体，不改微信、DNS、fake-ip、IPv6。
UPSTREAM_URL = "https://raw.githubusercontent.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/refs/heads/release/lazy_group.conf"

OUTPUT_FILE = Path("sr_lazy_group_ai.conf")
UPDATE_URL = "https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_lazy_group_ai.conf"

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

    return before + "\n".join(output) + after


def rebuild_ai_entry(line: str) -> str:
    """
    保留上游 AI = select,... 的原有选项，只插入 AI-优先 和 AI-其他。
    AI-优先放在 select 后第一位；
    AI-其他放在 PROXY / DIRECT / REJECT 之前。
    """
    _, _, value = line.partition("=")
    parts = [item.strip() for item in value.split(",") if item.strip()]

    if not parts:
        return "AI = select,AI-优先,AI-其他,PROXY,DIRECT"

    group_type = parts[0]
    choices = parts[1:]

    # 防止脚本重复运行后重复插入。
    choices = [item for item in choices if item not in {"AI-优先", "AI-其他"}]

    new_choices = ["AI-优先"]
    inserted_other = False
    fallback_names = {"PROXY", "Proxy", "proxy", "DIRECT", "Direct", "direct", "REJECT", "Reject", "reject"}

    for item in choices:
        if not inserted_other and item in fallback_names:
            new_choices.append("AI-其他")
            inserted_other = True
        new_choices.append(item)

    if not inserted_other:
        new_choices.append("AI-其他")

    return "AI = " + ",".join([group_type] + new_choices)


def enhance_ai_group(config: str) -> str:
    before, section, after = get_section(config, "[Proxy Group]")
    lines = section.splitlines()
    output = []
    replaced_ai = False

    for line in lines:
        stripped = line.strip()

        # 删除脚本旧版本插入的 AI-优先 / AI-其他，避免重复。
        if re.match(r"^AI-优先\s*=", stripped):
            continue
        if re.match(r"^AI-其他\s*=", stripped):
            continue

        if re.match(r"^AI\s*=", stripped):
            output.append(rebuild_ai_entry(stripped))
            output.append("")
            output.append("# AI 优先入口：只收录标准台湾前缀节点")
            output.append(AI_PRIORITY_GROUP)
            output.append("")
            output.append("# AI 其他入口：排除已归类地区、上游区域策略组和订阅信息节点")
            output.append(AI_OTHER_GROUP)
            replaced_ai = True
            continue

        output.append(line)

    if not replaced_ai:
        raise ValueError("Missing AI entry in [Proxy Group]. Upstream lazy_group.conf may have changed.")

    return before + "\n".join(output) + after


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
