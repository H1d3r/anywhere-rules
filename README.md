# Anywhere Rules

Anywhere 可订阅规则库。仓库会通过 GitHub Actions 自动拉取上游规则，转换成 Anywhere Routing Rule Set 的 `.arrs` 文本格式。

## 关于 Anywhere

[Anywhere](https://github.com/NodePassProject/Anywhere) 一款完全基于 Swift 开发的原生零依赖代理客户端。无 Electron，无 WebView，非 sing-box 壳程序。从底层实现纯协议封装。支持 vless、trojan、hysteria、shadowsocks、http 等多种主流协议。同时兼顾稳定与性能。

## 目录

- `rules/common/`：常用规则集，适合大多数用户直接订阅。
- `rules/all/`：blackmatrix7/ios_rule_script 的 Surge 规则全量转换，适合需要细分服务规则的用户。
- `rules/common/catalog.md`：常用规则目录。
- `rules/catalog.md`：全量规则目录。

## 订阅链接

常用规则：

```text
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/rules/common/AI.arrs
```

全量规则：

```text
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/rules/all/Apple/Apple.arrs
```

在 Anywhere 中填入对应 `.arrs` 链接即可。

## 自动更新

`.github/workflows/update-rules.yml` 每天 04:18（Asia/Shanghai）运行一次，也支持手动触发。更新流程：

1. 转换 blackmatrix7 全量 Surge 规则到 `rules/all/`。
2. 按常用规则组合生成 `rules/common/`。
3. 如果生成结果有变化，自动提交到仓库。

## 说明

Anywhere 当前支持域名后缀、域名关键词、IPv4 CIDR、IPv6 CIDR。上游中的 `URL-REGEX`、`PROCESS-NAME`、`USER-AGENT`、`IP-ASN` 等无法等价表达的规则会被跳过，并写入生成文件头部的 `SKIPPED` / `SKIPPED-TYPES`。

## 致谢

感谢以下规则项目与作者长期维护公开规则，本仓库仅做格式转换与整理：

- blackmatrix7/ios_rule_script
- ACL4SSR/ACL4SSR
- SukkaW/Surge
- ConnersHua/RuleGo
- NobyDa/Script
- Loyalsoldier/v2ray-rules-dat
- Loyalsoldier/surge-rules
- TG-Twilight/AWAvenue-Ads-Rule
- limbopro/Adblock4limbo
- dler-io/Rules
- geekdada/surge-list
- VirgilClyne/GetSomeFries
