# shadowrocket-uzcc-rules

一套用于 Shadowrocket 的个人分流配置，核心目的是让 AI 服务走代理。提供两个版本：**完整规则版**和**香港轻量版**，按需选一个用即可。

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

完整规则版由脚本自动生成：拉取上游 `sr_cnip.conf` → 读取本仓库的 `uzcc_rules.txt` → 把 AI 规则插入配置 → 输出 `sr_cnip_ai_routing.conf`，再由 GitHub Actions 定期更新。香港轻量版为手动维护。

## 文件说明

|文件                            |说明                 |
|------------------------------|-------------------|
|`sr_cnip_ai_routing.conf`     |完整规则版配置            |
|`sr_ai_proxy_hk.conf`         |香港轻量版配置            |
|`uzcc_rules.txt`              |自定义 AI 分流规则        |
|`merge_rules.py`              |拉取并合并规则的脚本         |
|`.github/workflows/update.yml`|GitHub Actions 自动更新|
|`NOTICE.md`                   |第三方引用与授权说明         |
|`LICENSE`                     |许可证                |

## 第三方引用

- 完整规则版基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 Shadowrocket 规则生成。
- 部分 AI 规则通过远程 `RULE-SET` 引用 [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)。这些远程规则不会被复制进本仓库，仍遵循原项目许可证。

详见 [`NOTICE.md`](NOTICE.md)。

## 许可证

本仓库采用 **CC BY-SA 4.0**。原因是完整规则版属于上游规则的二次整理与再发布，沿用同一许可证以保持一致。再次分发时请保留署名并使用相同许可证。

## 注意事项

- 仓库不含任何节点、订阅、UUID、密码、Token 或账号信息，也不提供网络服务。
- 配置里的策略组名称需与你 Shadowrocket 中实际的策略组对应。
- 上游规则结构若变动，合并脚本可能需要相应调整。
- 请自行确认所在地法律法规及相关平台条款。
