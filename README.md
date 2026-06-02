# shadowrocket-uzcc-rules

一套用于 Shadowrocket 的个人分流配置。提供两个版本：**完整规则版**和**香港轻量版**，按需选择。

## 使用方法

Shadowrocket →「配置」→ 右上角「+」→ 类型选「配置」→ 粘贴下方任一地址 → 下载并启用 → 选择代理节点。

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
基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `lazy_group.conf` 生成。它完整保留上游默认分流逻辑，只增强 AI 策略组。适合作为主力配置长期使用。

**香港轻量版（`sr_ai_proxy_hk.conf`）**  
为香港 SIM、eSIM 或本地网络设计。逻辑极简：只让 AI 服务走代理，Google、Microsoft 和其他流量保持直连。

## 完整规则版改了什么

完整规则版只改一个位置：`[Proxy Group]` 里的 AI 分组。

不会修改：

```text
[General]
[Rule]
DNS
fake-ip
IPv6
微信 / 视频号 / 公众号 / 小程序规则
上游默认分流规则
```

因此微信、国内 App、DNS、fake-ip 等逻辑继续由 Johnshall 的 `lazy_group.conf` 原样处理。

## AI 策略组增强

脚本会保留上游 `AI = select,...` 的原有选项，只新增：

```text
AI-优先
AI-其他
```

`AI-优先` 用于收录标准台湾前缀节点：

```text
台湾-
台灣-
TW-
Taiwan-
🇹🇼-
```

`AI-其他` 用于收录未命中台湾、香港、新加坡、日本、美国关键词的真实节点。

为避免把上游区域策略组当成真实节点，规则会排除：

```text
香港节点
台湾节点
台灣节点
日本节点
新加坡节点
韩国节点
韓國节点
美国节点
美國节点
```

也会排除订阅信息、流量提示、到期提示、官网入口等非节点内容。

## 工作原理

完整规则版由脚本自动生成：

```text
拉取上游 lazy_group.conf
→ 修改 update-url 为本仓库地址
→ 增强 AI 分组
→ 输出 sr_lazy_group_ai.conf
```

脚本不再使用 `uzcc_rules.txt`。

## 文件说明

| 文件                           | 说明                       |
| ------------------------------ | -------------------------- |
| `sr_lazy_group_ai.conf`        | 完整规则版配置             |
| `sr_ai_proxy_hk.conf`          | 香港轻量版配置             |
| `merge_rules.py`               | 拉取并增强完整规则版的脚本 |
| `.github/workflows/update.yml` | GitHub Actions 自动更新    |
| `NOTICE.md`                    | 第三方引用与授权说明       |
| `LICENSE`                      | 许可证                     |

## 生成方式

```bash
python3 merge_rules.py
```

生成结果：

```text
sr_lazy_group_ai.conf
```

## 第三方引用

完整规则版基于 [Johnshall / Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `lazy_group.conf` 生成。

详见 [`NOTICE.md`](NOTICE.md)。

## 许可证

本仓库采用 **CC BY-SA 4.0**。再次分发时请保留署名并使用相同许可证。

## 注意事项

- 仓库不含任何节点、订阅、UUID、密码、Token 或账号信息。
- `PROXY` 表示 Shadowrocket 当前默认代理出口，不需要额外定义同名策略组。
- 上游 `lazy_group.conf` 结构如果发生变化，`merge_rules.py` 可能需要同步调整。
