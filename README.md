# shadowrocket-uzcc-rules

一套用于 Shadowrocket 的个人分流配置，核心目的是让 AI 服务走代理，并尽量保持国内应用直连稳定。提供两个版本：**完整规则版**和**香港轻量版**，按需选一个用即可。

## 使用方法

Shadowrocket →「配置」→ 右上角「+」→ 类型选「配置」→ 粘贴下方任一地址 → 下载并启用 → 选好代理节点。

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
在 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 [`sr_cnip.conf`](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf) 上叠加自定义 AI 规则，保留完整的国内外分流和 CNIP 规则，并支持自动更新。适合作为主力配置长期使用。

**香港轻量版（`sr_ai_proxy_hk.conf`）**
为香港 SIM、eSIM 或本地网络设计，逻辑极简：只有 AI 服务走代理，Google、Microsoft 及其余流量全部直连。

不想折腾复杂规则、只要 AI 分流的，选香港轻量版；想要完整分流的，选完整规则版。

## 工作原理

完整规则版由脚本自动生成：拉取上游 `sr_cnip.conf` → 修正上游 `bypass-tun` 中可能影响 fake-ip 中继的 `198.18.0.0/15` → 为微信/腾讯资源域名注入 `always-real-ip` → 读取本仓库的 `uzcc_rules.txt` → 把 AI 规则和自定义规则插入配置 → 输出 `sr_cnip_ai_routing.conf`，再由 GitHub Actions 定期更新。香港轻量版为手动维护。

## 完整规则版特性

- **AI 独立分流**：OpenAI、Claude、Anthropic、Sora、Perplexity、Poe、Grok 等服务走 `AI` 策略组。
- **AI 节点自动归类**：按节点名称自动生成台湾、香港、新加坡、日本、美国等分组；`AI-优先` 只收录 `台湾- / 台灣- / TW- / Taiwan- / 🇹🇼-` 这类标准前缀节点。
- **默认代理出口可选**：`AI` 组内保留 `PROXY`，表示跟随 Shadowrocket 当前默认代理出口；也可手动选择地区组或 `DIRECT`。
- **微信直连修复**：通过 WeChat 规则集让微信相关域名直连，并对微信/腾讯图片、头像、小程序、支付等资源域名注入 `always-real-ip`，降低 fake-ip 场景下图片白图或资源加载失败的概率。
- **fake-ip 中继修正**：自动从上游 `bypass-tun` 中移除 `198.18.0.0/15`，避免 fake-ip 地址绕过 TUN 导致映射失效。
- **IPv6 策略保持上游逻辑**：不额外关闭 IPv6；如上游配置为 `ipv6 = true`、`prefer-ipv6 = false`，表示接管 IPv6 但不优先使用 IPv6 回源。
- **DNS 不做激进修改**：不强行改为境外 DNS，也不添加 ChinaMax；优先保持通用稳定性。

## 文件说明

| 文件                           | 说明                                                         |
| ------------------------------ | ------------------------------------------------------------ |
| `sr_cnip_ai_routing.conf`      | 完整规则版配置                                               |
| `sr_ai_proxy_hk.conf`          | 香港轻量版配置                                               |
| `uzcc_rules.txt`               | 自定义规则，包含 AI 分流与 WeChat 直连规则                   |
| `merge_rules.py`               | 拉取、修正并合并规则的脚本，包含 fake-ip 与微信 real-ip 处理 |
| `.github/workflows/update.yml` | GitHub Actions 自动更新                                      |
| `NOTICE.md`                    | 第三方引用与授权说明                                         |
| `LICENSE`                      | 许可证                                                       |

## 第三方引用

- 完整规则版基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 Shadowrocket 规则生成。
- 部分 AI 规则和 WeChat 直连规则通过远程 `RULE-SET` 引用 [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)。这些远程规则不会被复制进本仓库，仍遵循原项目许可证。

详见 [`NOTICE.md`](NOTICE.md)。

## 许可证

本仓库采用 **CC BY-SA 4.0**。原因是完整规则版属于上游规则的二次整理与再发布，沿用同一许可证以保持一致。再次分发时请保留署名并使用相同许可证。

## 注意事项

- 仓库不含任何节点、订阅、UUID、密码、Token 或账号信息，也不提供网络服务。
- 完整规则版中的 `PROXY` 使用 Shadowrocket 的默认代理出口语义；AI 组选择 `PROXY` 时会跟随当前默认代理节点。
- `always-real-ip` 只针对微信/腾讯相关域名，不是全局关闭 fake-ip。
- 配置里的自定义策略组由完整规则版自动注入；如自行改名，请同步修改规则里的策略名。
- 上游规则结构若变动，合并脚本可能需要相应调整。
- 请自行确认所在地法律法规及相关平台条款。
