# shadowrocket-uzcc-rules

本仓库用于维护适用于 Shadowrocket 的个人分流配置，包含完整规则版与香港网络轻量版两个配置入口，主要用于 AI 服务分流、规则订阅管理和配置自动更新。
仓库目前提供两个配置入口：

1. **完整规则版：`sr_cnip_ai_routing.conf`**  
   基于 Johnshall / Shadowrocket-ADBlock-Rules-Forever 的 `sr_cnip.conf` 生成，并叠加自定义 AI 分流规则。适合需要完整国内外分流、CNIP 规则和自动更新能力的用户。

2. **香港网络轻量版：`sr_ai_proxy_hk.conf`**  
   面向香港 SIM、香港 eSIM、香港手机卡或香港本地网络环境。核心逻辑是 AI 服务走代理，Google、Microsoft 和其他流量直连。

## 配置订阅地址

### 1. 完整规则版

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_cnip_ai_routing.conf
```

适合需要完整规则的用户。

主要逻辑：

- 保留上游 `sr_cnip.conf` 的基础分流结构
- 叠加自定义 AI 分流规则
- 支持 GitHub Actions 自动更新
- 适合长期作为主配置使用

### 2. 香港网络轻量版

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_ai_proxy_hk.conf
```

适合使用香港 SIM、香港 eSIM、香港手机卡或香港本地网络的用户。

主要逻辑：

- AI 服务走代理
- Google 系服务直连
- Microsoft 系服务直连
- 其他流量默认直连

## 两个版本怎么选

| 使用需求 | 推荐配置 |
|---|---|
| 想使用完整国内外分流、CNIP 规则和较完整的基础规则 | `sr_cnip_ai_routing.conf` |
| 处于香港网络，只想让 AI 服务走代理 | `sr_ai_proxy_hk.conf` |
| 不想使用复杂规则，只想保留轻量 AI 分流 | `sr_ai_proxy_hk.conf` |

## 仓库文件说明

| 文件 | 说明 |
|---|---|
| `sr_cnip_ai_routing.conf` | 完整规则版 Shadowrocket 配置 |
| `sr_ai_proxy_hk.conf` | 香港网络轻量版 Shadowrocket 配置 |
| `uzcc_rules.txt` | 自定义 AI 分流规则 |
| `merge_rules.py` | 自动拉取并合并规则的脚本 |
| `.github/workflows/update.yml` | GitHub Actions 自动更新配置 |
| `README.md` | 项目说明 |
| `NOTICE.md` | 第三方项目引用和授权说明 |
| `LICENSE` | 本仓库许可证 |

## 使用方法

1. 打开 Shadowrocket。
2. 进入「配置」。
3. 点击右上角「+」。
4. 类型选择「配置」。
5. 粘贴上方 Raw 订阅地址。
6. 下载并启用配置。
7. 根据实际情况选择对应的代理策略或节点。

## 工作原理

完整规则版通过自动合并脚本完成以下操作：

1. 拉取上游 `sr_cnip.conf`。
2. 读取本仓库的 `uzcc_rules.txt`。
3. 将自定义 AI 规则插入到 Shadowrocket 配置中。
4. 生成最终的 `sr_cnip_ai_routing.conf`。
5. 通过 GitHub Actions 定期更新。

香港网络轻量版为独立维护的配置文件，不依赖自动合并脚本。

## 第三方项目引用

本仓库可能引用或基于以下项目：

- Johnshall / Shadowrocket-ADBlock-Rules-Forever
- blackmatrix7 / ios_rule_script

其中，完整规则版基于 Johnshall 的 Shadowrocket 规则生成；部分 AI 规则可能通过远程 `RULE-SET` 引用 blackmatrix7 / ios_rule_script。本仓库不会将 blackmatrix7 的远程规则文件复制、合并或重新分发到仓库内，相关规则内容仍以原项目许可证为准。

详细说明见 `NOTICE.md`。

## 许可证

本仓库整体采用 **Creative Commons Attribution-ShareAlike 4.0 International License（CC BY-SA 4.0）**。

选择该许可证的原因是：完整规则版属于基于上游 Shadowrocket 规则的二次整理与再发布，为保持授权口径一致，本仓库统一采用 CC BY-SA 4.0。

使用、修改或再发布本仓库内容时，请保留原作者与本仓库的署名，并以相同许可证继续分享。

## 注意事项

- 本仓库不包含任何代理节点、机场订阅、UUID、密码、Token 或账号信息。
- 本仓库仅提供 Shadowrocket 配置和分流规则，不提供网络服务。
- 配置中的策略组名称需要与 Shadowrocket 中实际存在的策略组或代理策略相匹配。
- 若上游规则结构发生变化，自动合并脚本可能需要调整。
- 使用者应自行确认所在地法律法规、网络服务商规则和相关平台服务条款。
