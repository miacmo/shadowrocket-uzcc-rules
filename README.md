# shadowrocket-uzcc-rules

本仓库用于在 Johnshall 的 Shadowrocket 分流规则基础上，增加一层面向 AI 服务的自定义分流规则，生成适用于 Shadowrocket 的订阅配置文件。

本仓库的重点是 **AI 分流**：在保留原作者 `sr_cnip` 规则更新能力的前提下，将部分常用 AI 服务单独分流到 `AI` 分组，再由用户按地区节点选择出口。

## 规则链接

### 订阅规则

Shadowrocket 订阅地址：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_cnip_ai_routing.conf
```

### 原作者规则

本仓库基于 Johnshall 的 `sr_cnip.conf` 规则进行二次合并：

```text
https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf
```

### 本仓库地址

```text
https://github.com/miacmo/shadowrocket-uzcc-rules
```

## 原规则来源

本项目基于以下原作者规则进行二次合并：

- 原作者项目：Johnshall / Shadowrocket-ADBlock-Rules-Forever
- 原规则地址：https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf
- 原项目地址：https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever

感谢原作者 Johnshall 对 Shadowrocket 分流规则的长期维护。本仓库仅用于个人自定义规则合并，不声明对原规则的所有权。

## 本仓库的作用

本仓库通过 GitHub Actions 定时拉取原作者最新规则，并将本仓库中的 AI 分流规则插入到原规则 `[Rule]` 段之前，从而实现：

1. 保留原作者 `sr_cnip` 规则的持续更新；
2. 将部分常用 AI 服务单独分流到 `AI` 分组；
3. 通过地区分组选择不同出口节点；
4. 避免每次更新订阅后手动修改配置；
5. 自动生成最终可供 Shadowrocket 订阅的配置文件。

## 当前 AI 分流逻辑

当前自定义规则主要实现以下逻辑：

1. 部分常用 AI 服务走 `AI` 分组；
2. `AI` 分组下再选择 `AI-台湾`、`AI-香港`、`AI-新加坡`、`AI-日本`、`AI-美国`、`AI-其他`；
3. 各地区分组按节点名称自动匹配；
4. 节点名称中包含 `剩余`、`流量`、`到期`、`套餐` 的项目会被排除；
5. Bing 强制直连；
6. Gemini 不加入本仓库的 AI 分流规则，继续使用原作者规则；
7. Microsoft Copilot / 微软 AI 不加入本仓库的 AI 分流规则，继续使用原作者规则；
8. Canva 不加入本仓库的 AI 分流规则，继续使用原作者规则；
9. Google 系服务不在自定义规则中覆盖，继续使用原作者规则；
10. 其他网站继续使用原作者规则；
11. 每天北京时间 10:00 自动拉取原作者规则并重新合并。

最终规则逻辑如下：

```text
指定 AI 服务 → AI → 地区分组 → 具体节点
Bing → DIRECT
Gemini / Google 系 AI → 原作者规则
Microsoft Copilot / 微软 AI → 原作者规则
Canva → 原作者规则
Google 系服务 → 原作者规则
其他国外网站 → 原作者规则
国内网站 → 原作者规则
```

## 地区分组说明

`AI` 分组下包含以下地区出口：

```text
AI-台湾
AI-香港
AI-新加坡
AI-日本
AI-美国
AI-其他
```

各地区分组会根据节点名称进行匹配。例如节点名称中包含 `台湾`、`TW`、`Taiwan` 的节点会进入 `AI-台湾` 分组；节点名称中包含 `香港`、`HK`、`Hong Kong` 的节点会进入 `AI-香港` 分组。

`AI-其他` 用于收纳未命中台湾、香港、新加坡、日本、美国关键词的其他节点。

为避免订阅信息类节点进入分组，以下关键词会被排除：

```text
剩余
流量
到期
套餐
```

## 文件说明

```text
merge_rules.py
```

用于拉取原作者规则，并将自定义代理分组和自定义规则合并进去。

```text
uzcc_rules.txt
```

自定义规则文件。该文件只写规则本体，不需要写 `[Rule]`。

```text
.github/workflows/update.yml
```

GitHub Actions 自动更新配置。当前设置为每天北京时间 10:00 自动运行。

```text
sr_cnip_ai_routing.conf
```

自动生成的最终 Shadowrocket 配置文件，也是 Shadowrocket 实际订阅的文件。

## 自动更新机制

GitHub Actions 会在每天北京时间 10:00 自动执行以下步骤：

1. 拉取原作者最新规则；
2. 读取本仓库的 `uzcc_rules.txt`；
3. 插入自定义代理分组；
4. 将自定义规则插入到原作者规则之前；
5. 生成并提交 `sr_cnip_ai_routing.conf`。

也可以在 GitHub 仓库中手动运行：

```text
Actions → Update Shadowrocket Rules → Run workflow
```

## 使用方式

在 Shadowrocket 中添加配置订阅，填入：

```text
https://raw.githubusercontent.com/miacmo/shadowrocket-uzcc-rules/main/sr_cnip_ai_routing.conf
```

添加后更新配置即可。

## 注意事项

本仓库仅用于个人学习和自用配置管理。

原始规则的维护、更新和版权归原作者所有。本仓库只是基于原作者规则进行个人化合并，不对原规则内容主张所有权。

本仓库不应提交任何节点链接、订阅链接、UUID、密码、Token 或其他敏感信息。

如果原作者规则结构发生重大变化，本仓库的合并脚本可能需要相应调整。
