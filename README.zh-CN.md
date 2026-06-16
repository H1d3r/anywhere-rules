# Anywhere Rules

适用于 [Anywhere](https://github.com/NodePassProject/Anywhere) 的规则库，基于公开规则源转换为可导入的 `.arrs` 和 `.amrs` 文件。

[English](README.md)

## 关于 Anywhere

[Anywhere](https://github.com/NodePassProject/Anywhere) 是一款完全基于 Swift 开发的原生零依赖代理客户端。无 Electron，无 WebView，非 sing-box 壳程序。从底层实现纯协议封装，支持 vless、trojan、hysteria、shadowsocks、http 等多种主流协议，同时兼顾稳定与性能。

## 内容

- `rules/common/`：常用路由规则集。
- `rules/all/`：blackmatrix7 全量转换路由规则集，超过 100,000 条的规则会自动切片。
- `mitm/`：实验性 MITM 规则集及相关 Reject 规则集。

## 使用

### 路由规则

在 Anywhere 中导入 `.arrs` Raw 链接，然后将规则集分配给 `DIRECT`、`REJECT` 或代理策略。

```text
https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AI.arrs
```

Anywhere 的规则文件只包含名称和匹配规则，具体动作需要在 App 内为整个规则集设置。

### MITM 规则

MITM 规则为实验性内容，仅供学习交流。

将 `.amrs` 文件导入 Anywhere 的 MITM 规则集。部分 MITM 规则还需要搭配 Reject 规则，例如将 `mitm/DomainReject.arrs` 作为路由规则集导入，并分配给 `REJECT`。

请只在你有权检查的流量上启用 MITM。

## 常用规则

推荐策略只是起点，请按自己的代理配置调整。

| 规则 | 数量 | 建议策略 | 用途 | Raw |
| --- | ---: | --- | --- | --- |
| `Reject` | 6204 | `REJECT` | 广告、恶意站点和跟踪拦截基础集合。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Reject.arrs) |
| `Ads_AWAvenue` | 899 | `REJECT` | 秋风广告规则 AWAvenue。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Ads_AWAvenue.arrs) |
| `AI` | 49 | 代理 | 常见 AI 服务。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AI.arrs) |
| `Proxy` | 1559 | 代理 | 常用代理域名集合。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Proxy.arrs) |
| `ProxyGFW` | 7597 | 代理 | GFW 代理集合。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/ProxyGFW.arrs) |
| `GFW` | 4252 | 代理 | GFW 域名列表。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/GFW.arrs) |
| `Direct` | 36 | `DIRECT` | 常用直连补充。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Direct.arrs) |
| `AppleCN` | 9 | `DIRECT` | 苹果中国和苹果 CDN 直连。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AppleCN.arrs) |
| `AppleProxy` | 39 | 代理 | 通常需要代理的苹果服务。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AppleProxy.arrs) |
| `Apple` | 44 | 按需 | 苹果基础服务。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Apple.arrs) |
| `AppleServices` | 17 | 按需 | 苹果系统服务。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AppleServices.arrs) |
| `AppleMusic` | 9 | 按需 | Apple Music。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/AppleMusic.arrs) |
| `Google` | 25 | 代理 | Google 服务。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Google.arrs) |
| `YouTube` | 14 | 代理 | YouTube。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/YouTube.arrs) |
| `Microsoft` | 79 | 按需 | Microsoft 服务。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Microsoft.arrs) |
| `GitHub` | 6 | 按需 | GitHub。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/GitHub.arrs) |
| `OneDrive` | 15 | 按需 | OneDrive。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/OneDrive.arrs) |
| `Telegram` | 45 | 代理 | Telegram 域名与 IP。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Telegram.arrs) |
| `Telegram_NoIP` | 30 | 代理 | Telegram 域名，不含 IP。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Telegram_NoIP.arrs) |
| `Twitter` | 12 | 代理 | X / Twitter。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Twitter.arrs) |
| `Instagram` | 4 | 代理 | Instagram。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Instagram.arrs) |
| `Facebook` | 21 | 代理 | Facebook。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Facebook.arrs) |
| `Netflix` | 40 | 代理 | Netflix。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Netflix.arrs) |
| `Disney` | 172 | 代理 | Disney+。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Disney.arrs) |
| `Spotify` | 29 | 代理 | Spotify。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Spotify.arrs) |
| `TikTok` | 81 | 代理 | TikTok。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/TikTok.arrs) |
| `Bilibili` | 20 | `DIRECT` | Bilibili。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Bilibili.arrs) |
| `WeChat` | 339 | `DIRECT` | WeChat。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/WeChat.arrs) |
| `ChinaDomain` | 857 | `DIRECT` | 中国大陆常见域名直连。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/ChinaDomain.arrs) |
| `CN_Additional` | 43245 | `DIRECT` | 中国大陆域名补充。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/CN_Additional.arrs) |
| `Geosite_CN` | 4752 | `DIRECT` | 从 geosite.dat 的 `GEOLOCATION-CN` 提取的中国大陆域名。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Geosite_CN.arrs) |
| `ChinaIP` | 5711 | `DIRECT` | 中国大陆 IP CIDR。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/ChinaIP.arrs) |
| `GeoIP_CN` | 5875 | `DIRECT` | 从 Country.mmdb 提取的中国大陆 IP CIDR。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/GeoIP_CN.arrs) |
| `Lan` | 8 | `DIRECT` | 局域网和私有地址。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Lan.arrs) |
| `Game` | 597 | 按需 | 游戏平台集合。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Game.arrs) |
| `Steam` | 54 | 按需 | Steam。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Steam.arrs) |
| `PayPal` | 247 | 按需 | PayPal。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/PayPal.arrs) |
| `Cloudflare` | 65 | 按需 | Cloudflare。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/Cloudflare.arrs) |
| `CDN` | 4526 | `DIRECT` | CDN 直连辅助。 | [Raw](https://raw.githubusercontent.com/chikacya/anywhere-rules/main/rules/common/CDN.arrs) |

## 更新

GitHub Actions 每天自动更新生成规则。流程会转换 blackmatrix7 规则、生成 common 规则，从 `Country.mmdb` 提取 `GeoIP_CN`，并从 `geosite.dat` 提取 `Geosite_CN`。

## 说明

Anywhere 路由规则集当前支持域名后缀、域名关键词、IPv4 CIDR 和 IPv6 CIDR。上游中无法等价表达的规则类型会在转换时跳过。

Anywhere 单个自定义规则集最多 100,000 条规则。本仓库会自动将超限规则集拆成编号分片。

## 致谢

感谢以下公开规则与脚本项目/作者的长期维护：

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
- 等
