# shadowrocket-uzcc-rules

在 Johnshall 的 Shadowrocket 分流规则基础上，叠加一层面向海外 AI 服务的自定义分流，自动生成可供 Shadowrocket 订阅的配置文件。

本仓库的重点是 **AI 分流**：在保留原作者 `sr_cnip` 规则持续更新的前提下，把部分常用海外 AI 服务单独分流到 `AI` 分组，再由用户按地区节点选择出口。

## 工作原理

GitHub Actions 每天北京时间 10:00 自动执行以下步骤：

1. 拉取原作者最新规则；
2. 读取本仓库的 `uzcc_rules.txt`；
3. 插入自定义代理分组；
4. 将自定义规则插入到原作者规则 `[Rule]` 段之前；
5. 生成并提交 `sr_cnip_ai_routing.conf`。

这样既能跟随原作者规则更新，又无需在每次更新订阅后手动改配置。也可在仓库中手动触发：`Actions → Update Shadowrocket Rules → Run workflow`。

## 分流逻辑

| 流量 | 走向 |
| --- | --- |
| 指定海外 AI 服务 | `AI` → 地区分组 → 具体节点 |
| Bing | 强制直连（DIRECT） |
| Gemini、Google 系服务、Microsoft Copilot、Canva、中国 AI 服务 | 维持原作者规则 |
| 其余国内外网站 | 维持原作者规则 |

也就是说，本仓库只额外接管「指定海外 AI 服务」和「Bing」，其他一律不覆盖，沿用原作者规则。

## 地区分组

`AI` 分组下按出口地区进一步划分：

```text
AI-台湾 / AI-香港 / AI-新加坡 / AI-日本 / AI-美国 / AI-其他
```

各分组根据节点名称中的关键词自动匹配，例如含 `台湾 / TW / Taiwan` 的节点进入 `AI-台湾`，含 `香港 / HK / Hong Kong` 的进入 `AI-香港`。未命中上述五个地区关键词的节点归入 `AI-其他`。

为避免订阅信息类节点混入分组，名称中含以下关键词的项目会被排除：

```text
剩余 / 流量 / 到期 / 套餐
```

## 使用方式

在 Shadowrocket 中添加配置订阅，填入：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_cnip_ai_routing.conf
```

添加后更新配置即可。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `merge_rules.py` | 拉取原作者规则，并合并自定义代理分组和自定义规则 |
| `uzcc_rules.txt` | 自定义规则本体，只写规则、无需 `[Rule]` 段 |
| `.github/workflows/update.yml` | GitHub Actions 自动更新配置（每天北京时间 10:00） |
| `sr_cnip_ai_routing.conf` | 自动生成、供 Shadowrocket 实际订阅的配置文件 |

## 原规则来源

本项目基于 Johnshall 的规则二次合并，感谢原作者长期维护：

- 原项目：<https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever>
- 原规则：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf>

## 注意事项

- 本仓库仅用于个人学习和自用配置管理，不对原规则内容主张所有权；原规则的维护、更新与版权均归原作者所有。
- 本仓库不应提交任何节点链接、订阅链接、UUID、密码、Token 等敏感信息。
- 若原作者规则结构发生重大变化，合并脚本可能需要相应调整。
