# shadowrocket-uzcc-rules

一套用于 Shadowrocket 的个人分流配置。提供两个版本：**完整规则版**和**香港轻量版**，按需选一个用即可。

## 使用方法

Shadowrocket →「配置」→ 右上角「+」→ 类型选「配置」→ 粘贴下方任一地址 → 下载并启用 → 选好代理节点。

完整规则版：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_lazy_group_ai.conf
```

香港轻量版：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_ai_proxy_hk.conf
```

## 两个版本怎么选

**完整规则版（`sr_lazy_group_ai.conf`）**  
基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `lazy_group.conf` 生成。保留上游完整策略组和默认分流逻辑，只增强 AI 分流区域。适合作为主力配置长期使用。

完整规则版的主要逻辑是：AI 服务优先命中 `AI` 策略组；国内域名通过 ChinaMax 统一直连；其余规则继续交给上游 `lazy_group.conf` 处理。

**香港轻量版（`sr_ai_proxy_hk.conf`）**  
为香港 SIM、eSIM 或本地网络设计，逻辑极简：只有 AI 服务走代理，Google、Microsoft 及其余流量全部直连。

不想折腾复杂规则、只要 AI 分流的，选香港轻量版；想要完整策略组和上游默认分流能力的，选完整规则版。

## AI 策略组增强

完整规则版保留上游 `lazy_group.conf` 原有策略组，只对 AI 分流区域做增强。

AI 入口为：

```ini
AI = select,AI-优先,AI-台湾,AI-香港,AI-新加坡,AI-日本,AI-美国,AI-其他,PROXY,DIRECT
```

其中：

- `AI-优先`：只收录命名为 `台湾-`、`台灣-`、`TW-`、`Taiwan-`、`🇹🇼-` 这类标准前缀的台湾节点。
- `AI-台湾`、`AI-香港`、`AI-新加坡`、`AI-日本`、`AI-美国`：沿用上游地区策略组。
- `AI-其他`：未命中上述地区关键词的真实节点。
- `PROXY`：Shadowrocket 当前默认代理出口。
- `DIRECT`：直连。

为避免把上游区域策略组当作真实节点，`AI-优先` 和 `AI-其他` 会排除：

```text
香港节点、台湾节点、台灣节点、日本节点、新加坡节点、韩国节点、韓國节点、美国节点、美國节点
```

同时也会排除订阅信息、流量提示、到期提示、官网入口等非节点项。

## 自定义规则顺序

完整规则版会把 `uzcc_rules.txt` 插入到上游 `[Rule]` 顶部，因此优先级高于上游规则。

当前自定义规则顺序为：

```text
Bing / Copilot → DIRECT
OpenAI / ChatGPT → AI
Claude / Anthropic → AI
Sora / Perplexity / Poe / Grok / xAI / Groq → AI
ChinaMax → DIRECT
上游 lazy_group.conf 默认规则
```

ChinaMax 放在 AI 规则之后、上游规则之前。这样 AI 服务优先走 AI 策略组，国内域名继续统一直连。

## 工作原理

完整规则版由脚本自动生成：

```text
拉取上游 lazy_group.conf
→ 增强 AI 分组
→ 插入 uzcc_rules.txt
→ 输出 sr_lazy_group_ai.conf
```

脚本不重构上游主体规则，不单独维护微信、视频号、公众号、小程序等域名清单，也不修改上游 DNS、fake-ip、IPv6 等通用逻辑。

香港轻量版为手动维护，不参与完整规则版的自动合并逻辑。

## 文件说明

| 文件                           | 说明                               |
| ------------------------------ | ---------------------------------- |
| `sr_lazy_group_ai.conf`        | 完整规则版配置                     |
| `sr_ai_proxy_hk.conf`          | 香港轻量版配置                     |
| `uzcc_rules.txt`               | 自定义 AI 分流与 ChinaMax 直连规则 |
| `merge_rules.py`               | 拉取并合并完整规则版的脚本         |
| `.github/workflows/update.yml` | GitHub Actions 自动更新            |
| `NOTICE.md`                    | 第三方引用与授权说明               |
| `LICENSE`                      | 许可证                             |

## 生成方式

```bash
python3 merge_rules.py
```

生成结果：

```text
sr_lazy_group_ai.conf
```

## 第三方引用

- 完整规则版基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `lazy_group.conf` 生成。
- 国内域名直连规则引用 [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 的 ChinaMax 规则集。
- 部分 AI 规则通过远程 `RULE-SET` 引用 [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)。这些远程规则不会被复制进本仓库，仍遵循原项目许可证。

详见 [`NOTICE.md`](NOTICE.md)。

## 许可证

本仓库采用 **CC BY-SA 4.0**。原因是完整规则版属于上游规则的二次整理与再发布，沿用同一许可证以保持一致。再次分发时请保留署名并使用相同许可证。

## 注意事项

- 仓库不含任何节点、订阅、UUID、密码、Token 或账号信息，也不提供网络服务。
- 完整规则版基于上游 `lazy_group.conf`，上游结构变动时，合并脚本可能需要调整。
- `PROXY` 表示 Shadowrocket 当前默认代理出口，不需要额外定义同名策略组。
- 请自行确认所在地法律法规及相关平台条款。
