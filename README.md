# shadowrocket-uzcc-rules

一套用于 Shadowrocket 的个人分流配置，核心目的是让 AI 服务单独走代理。提供两个版本：**完整规则版**和**香港轻量版**，按需选一个用即可。

## 使用方法

Shadowrocket →「配置」→ 右上角「+」→ 类型选「配置」→ 粘贴下方任一地址 → 下载并启用 → 选好代理节点。

完整规则版：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_lazy_ai_routing.conf
```

香港轻量版：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_ai_proxy_hk.conf
```

## 两个版本怎么选

**完整规则版（`sr_lazy_ai_routing.conf`）**  
在 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的默认 Shadowrocket 规则基础上叠加自定义 AI 分流规则，保留上游对国内外网站、常用 App、国内服务和国外服务的基础分流逻辑，并额外加入 AI 独立策略组。适合作为主力配置长期使用。

完整规则版的主要逻辑是：AI 服务优先命中 `AI` 策略组；国内域名通过 ChinaMax 统一直连；国内 IP 继续直连；其他国外流量走 `PROXY` 默认代理出口。

**香港轻量版（`sr_ai_proxy_hk.conf`）**  
为香港 SIM、eSIM 或本地网络设计，逻辑极简：只有 AI 服务走代理，Google、Microsoft 及其余流量全部直连。

不想折腾复杂规则、只要 AI 分流的，选香港轻量版；想要完整分流、国内外网站都按规则处理的，选完整规则版。

## AI 策略组

完整规则版新增独立 AI 策略组：

```ini
AI = select,AI-优先,AI-台湾,AI-香港,AI-新加坡,AI-日本,AI-美国,AI-其他,PROXY,DIRECT
```

其中：

- `AI-优先`：只收录命名为 `台湾-`、`台灣-`、`TW-`、`Taiwan-`、`🇹🇼-` 这类标准前缀的台湾节点。
- `AI-台湾`、`AI-香港`、`AI-新加坡`、`AI-日本`、`AI-美国`：按节点名称自动归类。
- `AI-其他`：未命中上述地区关键词的节点。
- `PROXY`：Shadowrocket 当前默认代理出口。
- `DIRECT`：直连。

规则中的订阅信息、流量提示、到期提示、官网入口等节点会被排除，避免被误归类到 AI 策略组中。

## 工作原理

完整规则版由脚本自动生成：拉取上游默认 Shadowrocket 规则 → 修正必要的 `[General]` 参数 → 插入 AI 策略组 → 读取本仓库的 `uzcc_rules.txt` → 把自定义 AI 规则和 ChinaMax 直连规则插入到上游规则之前 → 输出 `sr_lazy_ai_routing.conf`，再由 GitHub Actions 定期更新。

香港轻量版为手动维护，不参与完整规则版的自动合并逻辑。

## 完整规则版的关键处理

完整规则版会强制启用 IPv6 接管，并关闭 IPv6 优先回源：

```ini
ipv6 = true
prefer-ipv6 = false
```

这表示 Shadowrocket 会接管 IPv6 流量，避免 IPv6 绕过 TUN；同时双栈域名不优先使用 IPv6 回源。

完整规则版还会从 `bypass-tun` 或 `tun-excluded-routes` 中移除：

```ini
198.18.0.0/15
```

该网段是 fake-ip 常用地址段，不应放在 TUN 绕行列表中。

国内域名统一通过 ChinaMax 直连：

```ini
RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/ChinaMax/ChinaMax.list,DIRECT
```

ChinaMax 放在 AI 规则之后、上游默认规则之前。这样 AI 服务先走 AI 策略组，国内网站和微信、视频号、公众号、小程序等国内服务继续按国内直连逻辑处理。

## 文件说明

| 文件                           | 说明                         |
| ------------------------------ | ---------------------------- |
| `sr_lazy_ai_routing.conf`      | 完整规则版配置               |
| `sr_ai_proxy_hk.conf`          | 香港轻量版配置               |
| `uzcc_rules.txt`               | 自定义 AI 分流与国内直连规则 |
| `merge_rules.py`               | 拉取并合并完整规则版的脚本   |
| `.github/workflows/update.yml` | GitHub Actions 自动更新      |
| `NOTICE.md`                    | 第三方引用与授权说明         |
| `LICENSE`                      | 许可证                       |

## 第三方引用

- 完整规则版基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 Shadowrocket 规则生成。
- 国内域名直连规则引用 [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 的 ChinaMax 规则集。
- 部分 AI 规则通过远程 `RULE-SET` 引用 [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)。这些远程规则不会被复制进本仓库，仍遵循原项目许可证。

详见 [`NOTICE.md`](NOTICE.md)。

## 许可证

本仓库采用 **CC BY-SA 4.0**。原因是完整规则版属于上游规则的二次整理与再发布，沿用同一许可证以保持一致。再次分发时请保留署名并使用相同许可证。

## 注意事项

- 仓库不含任何节点、订阅、UUID、密码、Token 或账号信息，也不提供网络服务。
- 配置里的策略组名称需与你 Shadowrocket 中实际的策略组对应。
- `PROXY` 表示 Shadowrocket 当前默认代理出口，不需要额外定义同名策略组。
- 上游规则结构若变动，合并脚本可能需要相应调整。
- 请自行确认所在地法律法规及相关平台条款。
