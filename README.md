# shadowrocket-uzcc-rules

一套用于 Shadowrocket 的个人分流配置，核心目标是：国内直连、国外代理、AI 服务单独分流，并尽量避免 IPv6 绕过 TUN。

提供两个版本：**完整规则版**和**香港轻量版**，按需选择即可。

## 使用方法

Shadowrocket →「配置」→ 右上角「+」→ 类型选择「配置」→ 粘贴下方任一地址 → 下载并启用 → 选择合适的代理节点。

完整规则版：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_cnip_ai_routing.conf
```

香港轻量版：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_ai_proxy_hk.conf
```

## 两个版本怎么选

**完整规则版（`sr_cnip_ai_routing.conf`）**

基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 [`sr_cnip.conf`](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf) 生成，在上游“国内直连、国外代理”的基础上叠加 AI 分流、微信直连和 IPv6 相关修正。适合作为主力配置长期使用。

**香港轻量版（`sr_ai_proxy_hk.conf`）**

为香港 SIM、eSIM 或香港本地网络设计，逻辑更轻：主要让 AI 服务走代理，其余流量尽量保持直连。不想使用完整国内外分流规则时，可以选择这个版本。

## 完整规则版的策略逻辑

- Bing / Microsoft Copilot：直连。
- WeChat / 微信：优先直连，减少微信、图片、小程序、登录接口被误代理的概率。
- OpenAI / ChatGPT、Claude / Anthropic、Sora、Perplexity、Poe、Grok / xAI / Groq：走 `AI` 策略组。
- 国内流量：继承上游规则与 `GEOIP,CN,DIRECT`，尽量直连。
- 其他国外流量：最终走 `PROXY`。

`AI` 策略组默认结构：

```ini
AI = select,AI-优先,AI-台湾,AI-香港,AI-新加坡,AI-日本,AI-美国,AI-其他,PROXY,DIRECT
```

其中：

- `AI-优先` 只收录 `台湾-`、`台灣-`、`TW-`、`Taiwan-`、`🇹🇼-` 这类标准前缀台湾节点。
- `AI-台湾 / AI-香港 / AI-新加坡 / AI-日本 / AI-美国` 按节点名称自动归类。
- `PROXY` 表示 Shadowrocket 当前默认代理出口。
- `DIRECT` 可用于临时直连测试。

策略组正则已排除常见订阅信息关键词：`剩余`、`流量`、`到期`、`套餐`、`Expire`、`Traffic`、`官网`、`订阅`、`Subscription`。

## IPv6 与 DNS 说明

完整规则版会强制保留：

```ini
ipv6 = true
prefer-ipv6 = false
```

含义是：让 Shadowrocket 接管 IPv6，避免公网 IPv6 绕过 TUN；同时在双栈场景下不优先使用 IPv6。这个设置不是全局封禁 IPv6，而是把 IPv6 纳入 Shadowrocket 管辖。

当前主配置不默认启用 `force-remote-dns`，也不默认启用 DNS-over-PROXY。原因是新版 Shadowrocket 配置思路下，代理策略本身通常会由代理链路处理解析；而 `force-remote-dns` 和 `dns-server = ...#proxy` 更适合作为个人实验配置，不适合作为主线默认项。

如果 DNS 泄露检测显示中国 DNS，不一定代表代理流量泄露。请优先确认：出口 IP 是否为代理节点、是否存在本机 IPv6 泄露、AI / 社交平台是否实际可用。

## 工作原理

完整规则版由脚本自动生成：拉取上游 `sr_cnip.conf` → 读取本仓库的 `uzcc_rules.txt` → 插入自定义策略组和规则 → 输出 `sr_cnip_ai_routing.conf`，再由 GitHub Actions 定期更新。

香港轻量版为手动维护，当前不在自动合并脚本的修改范围内。

## 文件说明

| 文件                           | 说明                          |
| ------------------------------ | ----------------------------- |
| `sr_cnip_ai_routing.conf`      | 完整规则版配置                |
| `sr_ai_proxy_hk.conf`          | 香港轻量版配置                |
| `uzcc_rules.txt`               | 自定义 AI / WeChat 等分流规则 |
| `merge_rules.py`               | 拉取并合并规则的脚本          |
| `.github/workflows/update.yml` | GitHub Actions 自动更新配置   |
| `NOTICE.md`                    | 第三方引用与授权说明          |
| `LICENSE`                      | 许可证                        |

## 第三方引用

- 完整规则版基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 Shadowrocket 规则生成。
- AI、WeChat 等远程规则通过 `RULE-SET` 引用 [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)。这些远程规则不会被复制进本仓库，仍遵循原项目许可证。

详见 [`NOTICE.md`](NOTICE.md)。

## 许可证

本仓库采用 **CC BY-SA 4.0**。完整规则版属于上游规则的二次整理与再发布，沿用同一许可证以保持一致。再次分发时请保留署名并使用相同许可证。

## 注意事项

- 仓库不含任何节点、订阅、UUID、密码、Token 或账号信息，也不提供网络服务。
- 配置里的策略组名称和节点命名会影响自动归类效果。
- 上游规则结构若变动，合并脚本可能需要相应调整。
- 请自行确认所在地法律法规及相关平台条款。
