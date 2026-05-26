# NOTICE

This repository maintains Shadowrocket configuration files and routing rules for configuration management and technical learning purposes.

## Project Maintainer

Maintainer: miacmo

Repository:

```text
https://github.com/miacmo/shadowrocket-uzcc-rules
```

## Included Configurations

This repository provides two Shadowrocket configuration entries:

1. `sr_cnip_ai_routing.conf`

   A complete Shadowrocket configuration generated from upstream `sr_cnip.conf` and additional custom AI routing rules.

2. `sr_ai_proxy_hk.conf`

   A lightweight Shadowrocket configuration for Hong Kong SIM, Hong Kong eSIM, Hong Kong mobile network, or Hong Kong local network environments.

## Third-party Sources

### 1. Johnshall / Shadowrocket-ADBlock-Rules-Forever

The complete configuration version, `sr_cnip_ai_routing.conf`, is based on the upstream Shadowrocket rules maintained by Johnshall.

Upstream project:

```text
https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever
```

Upstream rule reference:

```text
https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf
```

The derived configuration in this repository preserves attribution and is distributed under CC BY-SA 4.0 to comply with the upstream share-alike requirement.

### 2. blackmatrix7 / ios_rule_script

Some AI routing rules may reference remote `RULE-SET` files from blackmatrix7 / ios_rule_script.

Upstream project:

```text
https://github.com/blackmatrix7/ios_rule_script
```

At the time of writing, the blackmatrix7 / ios_rule_script project indicates GPL-2.0 licensing. This repository only references its remote rule-set URLs where applicable and does not copy, modify, merge, or redistribute the contents of those remote rule files.

The license of those remote rule files remains governed by the upstream project.

## Licensing Position

This repository uses CC BY-SA 4.0 as its repository-level license.

The license covers:

- README and documentation written for this repository
- Custom routing rules maintained in this repository
- Generated configuration files distributed in this repository, subject to upstream attribution and share-alike requirements

Third-party projects, remote rule files, and upstream repositories remain governed by their own licenses.

## No Proxy Service Included

This repository does not provide:

- proxy nodes
- subscription services
- account credentials
- UUIDs
- passwords
- tokens
- server addresses

It only provides Shadowrocket configuration files and routing rules.

## Disclaimer

This repository is provided for configuration management and technical learning purposes. Users are responsible for ensuring that their use complies with applicable laws, regulations, network service agreements, and platform terms of service.
