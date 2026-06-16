# Anywhere Rules

Rule sets for [Anywhere](https://github.com/NodePassProject/Anywhere), converted from public rule sources into importable `.arrs` and `.amrs` files.

[简体中文](README.zh-CN.md)

## About Anywhere

[Anywhere](https://github.com/NodePassProject/Anywhere) is a native proxy client built entirely with Swift. It has no Electron, no WebView, and is not a sing-box wrapper. It implements protocols directly from the lower layers, supports vless, trojan, hysteria, shadowsocks, http, and other mainstream protocols, and focuses on stability and performance.

## Contents

- `rules/common/` - curated routing rule sets for daily use.
- `rules/all/` - full converted routing rule sets from blackmatrix7. Large rule sets are split into 100,000-rule chunks for Anywhere imports.
- `mitm/` - experimental MITM rule sets and related reject rule sets.

## Usage

### Routing Rules

Import a `.arrs` raw URL in Anywhere, then assign the imported rule set to `DIRECT`, `REJECT`, or a proxy policy.

```text
https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AI.arrs
```

Anywhere stores the action outside the file. A rule file only contains the rule set name and match rules.

### MITM Rules

MITM rules are experimental and are provided for learning and research only.

Import `.amrs` files into Anywhere MITM rule sets. Some MITM rules also need a matching reject rule set, such as `mitm/DomainReject.arrs`, imported as a routing rule set and assigned to `REJECT`.

Only enable MITM for traffic you are allowed to inspect.

## Common Rules

Suggested targets are only a starting point. Pick the policy that matches your own proxy setup.

| Rule | Rules | Suggested | Purpose | Raw |
| --- | ---: | --- | --- | --- |
| `Reject` | 6204 | `REJECT` | Basic ads, malicious sites, and tracking block list. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Reject.arrs) |
| `Ads_AWAvenue` | 899 | `REJECT` | AWAvenue ad-blocking rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Ads_AWAvenue.arrs) |
| `AI` | 49 | Proxy | Common AI services. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AI.arrs) |
| `Proxy` | 1559 | Proxy | General proxy-domain collection. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Proxy.arrs) |
| `ProxyGFW` | 7597 | Proxy | Broad GFW proxy collection. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/ProxyGFW.arrs) |
| `GFW` | 4252 | Proxy | GFW domain list. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/GFW.arrs) |
| `Direct` | 36 | `DIRECT` | Small direct-route supplement. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Direct.arrs) |
| `AppleCN` | 9 | `DIRECT` | Apple China and Apple CDN direct-route rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AppleCN.arrs) |
| `AppleProxy` | 39 | Proxy | Apple services that usually need a proxy. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AppleProxy.arrs) |
| `Apple` | 44 | As needed | Basic Apple service rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Apple.arrs) |
| `AppleServices` | 17 | As needed | Apple system service rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AppleServices.arrs) |
| `AppleMusic` | 9 | As needed | Apple Music rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AppleMusic.arrs) |
| `Google` | 25 | Proxy | Google services. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Google.arrs) |
| `YouTube` | 14 | Proxy | YouTube rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/YouTube.arrs) |
| `Microsoft` | 79 | As needed | Microsoft services. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Microsoft.arrs) |
| `GitHub` | 6 | As needed | GitHub rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/GitHub.arrs) |
| `OneDrive` | 15 | As needed | OneDrive rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/OneDrive.arrs) |
| `Telegram` | 45 | Proxy | Telegram domains and IP ranges. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Telegram.arrs) |
| `Telegram_NoIP` | 30 | Proxy | Telegram domains only, without IP ranges. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Telegram_NoIP.arrs) |
| `Twitter` | 12 | Proxy | X / Twitter rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Twitter.arrs) |
| `Instagram` | 4 | Proxy | Instagram rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Instagram.arrs) |
| `Facebook` | 21 | Proxy | Facebook rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Facebook.arrs) |
| `Netflix` | 40 | Proxy | Netflix rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Netflix.arrs) |
| `Disney` | 172 | Proxy | Disney+ rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Disney.arrs) |
| `Spotify` | 29 | Proxy | Spotify rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Spotify.arrs) |
| `TikTok` | 81 | Proxy | TikTok rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/TikTok.arrs) |
| `Bilibili` | 20 | `DIRECT` | Bilibili rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Bilibili.arrs) |
| `WeChat` | 339 | `DIRECT` | WeChat rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/WeChat.arrs) |
| `ChinaDomain` | 857 | `DIRECT` | Common mainland China domains. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/ChinaDomain.arrs) |
| `CN_Additional` | 43245 | `DIRECT` | Mainland China domain supplement. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/CN_Additional.arrs) |
| `Geosite_CN` | 4752 | `DIRECT` | Mainland China domains extracted from geosite.dat `GEOLOCATION-CN`. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Geosite_CN.arrs) |
| `ChinaIP` | 5711 | `DIRECT` | Mainland China IP CIDR rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/ChinaIP.arrs) |
| `GeoIP_CN` | 5875 | `DIRECT` | Mainland China IP CIDR rules extracted from Country.mmdb. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/GeoIP_CN.arrs) |
| `Lan` | 8 | `DIRECT` | LAN and private address rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Lan.arrs) |
| `Game` | 597 | As needed | Game platform rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Game.arrs) |
| `Steam` | 54 | As needed | Steam rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Steam.arrs) |
| `PayPal` | 247 | As needed | PayPal rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/PayPal.arrs) |
| `Cloudflare` | 65 | As needed | Cloudflare rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Cloudflare.arrs) |
| `CDN` | 4526 | `DIRECT` | CDN direct-route helper rules. | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/CDN.arrs) |

## Update

GitHub Actions updates generated rules daily. The workflow converts blackmatrix7 rules, builds common rules, extracts `GeoIP_CN` from `Country.mmdb`, and extracts `Geosite_CN` from `geosite.dat`.

## Notes

Anywhere routing rule sets currently support domain suffix, domain keyword, IPv4 CIDR, and IPv6 CIDR. Unsupported upstream rule types are skipped during conversion.

Each custom Anywhere rule set can contain at most 100,000 rules. This repository automatically splits larger generated rule sets into numbered parts.

## Thanks

Thanks to the upstream projects and authors who maintain public rules and scripts:

- blackmatrix7/ios_rule_script
- ACL4SSR/ACL4SSR
- SukkaW/Surge
- ConnersHua/RuleGo
- NobyDa/Script
- Loyalsoldier/v2ray-rules-dat
- Loyalsoldier/surge-rules
- Loyalsoldier/geoip
- TG-Twilight/AWAvenue-Ads-Rule
- limbopro/Adblock4limbo
- dler-io/Rules
- geekdada/surge-list
- fmz200/wool_scripts
- VirgilClyne/iRingo
- app2smile/rules
- and more
