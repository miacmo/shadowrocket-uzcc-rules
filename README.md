# shadowrocket-uzcc-rules

个人 Shadowrocket 分流配置,提供两个版本:**完整规则版**与**香港轻量版**。

## 使用方法

Shadowrocket →「配置」→ 右上角「+」→ 类型选「配置」→ 粘贴地址 → 下载启用 → 选择代理节点。

| 版本 | 地址 |
| --- | --- |
| 完整规则版 | `https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_lazy_group_ai.conf` |
| 香港轻量版 | `https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_ai_proxy_hk.conf` |

## 版本选择

**完整规则版（`sr_lazy_group_ai.conf`）** — 基于 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `lazy_group.conf`,完整保留上游分流逻辑,仅增强 AI 策略组。适合长期主力使用。

**香港轻量版（`sr_ai_proxy_hk.conf`）** — 为香港 SIM / eSIM / 本地网络设计。逻辑极简:仅 AI 服务走代理,Google、Microsoft 及其余流量直连。

## 完整规则版的改动

仅修改 `[Proxy Group]` 中的 AI 分组,不触碰 `[General]`、`[Rule]`、DNS、fake-ip、IPv6、微信/视频号/公众号/小程序及上游默认分流规则——这些继续由上游 `lazy_group.conf` 原样处理。

AI 分组在保留上游 `AI = select,...` 原有选项的基础上,新增两个子组:

- **优先节点**(置于 `香港节点` 之上):收录台湾前缀节点 `台湾-`、`台灣-`、`TW-`、`Taiwan-`、`🇹🇼-`。
- **其他节点**(置于最下方):收录未命中 台湾/香港/新加坡/日本/美国 关键词的真实节点。

为避免误收上游区域策略组与非节点内容,自动排除区域组名(`香港节点`、`台湾节点`、`日本节点`、`新加坡节点`、`韩国节点`、`美国节点` 等)以及订阅信息、流量/到期提示、官网入口等。

## 生成方式

```bash
python3 merge_rules.py
```

脚本流程:拉取上游 `lazy_group.conf` → 改写 `update-url` 为本仓库地址 → 增强 AI 分组 → 输出 `sr_lazy_group_ai.conf`。(不再使用 `uzcc_rules.txt`。)

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `sr_lazy_group_ai.conf` | 完整规则版配置 |
| `sr_ai_proxy_hk.conf` | 香港轻量版配置 |
| `merge_rules.py` | 拉取并增强完整规则版的脚本 |
| `.github/workflows/update.yml` | GitHub Actions 自动更新 |
| `NOTICE.md` | 第三方引用与授权说明 |
| `LICENSE` | 许可证 |

## 许可与引用

基于 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `lazy_group.conf` 生成,详见 [`NOTICE.md`](NOTICE.md)。本仓库采用 **CC BY-SA 4.0**,再分发请保留署名并沿用相同许可证。

## 注意事项

- 仓库不含任何节点、订阅、UUID、密码、Token 或账号信息。
- `PROXY` 表示 Shadowrocket 当前默认代理出口,无需额外定义同名策略组。
- 若上游 `lazy_group.conf` 结构变化,`merge_rules.py` 可能需同步调整。
