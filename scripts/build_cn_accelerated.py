#!/usr/bin/env python3
"""Build a CN domain supplement from dnsmasq-china-list accelerated domains."""

from __future__ import annotations

import argparse
import http.client
import ipaddress
import json
import re
import sqlite3
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode, urlparse

import maxminddb

from build_geosite_cn import DEFAULT_SOURCE_URL as DEFAULT_GEOSITE_URL
from build_geosite_cn import extract_rules as extract_geosite_rules
from build_geoip_cn import DEFAULT_SOURCE_URL as DEFAULT_MMDB_URL
from convert_blackmatrix7 import fetch_bytes


DEFAULT_SOURCE_URL = (
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/"
    "accelerated-domains.china.conf"
)
DEFAULT_DOH_ENDPOINTS = [
    "https://dns.alidns.com/resolve",
    "https://doh.pub/dns-query",
]
DEFAULT_ANYWHERE_RULES_DB_URL = (
    "https://raw.githubusercontent.com/NodePassProject/Anywhere/main/Shared/DataStore/Rules.db"
)
DNSMASQ_DOMAIN_RE = re.compile(r"^server=/([^/]+)/")
VALID_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)[a-z0-9.-]+(?<!-)$")
THREAD_STATE = threading.local()


@dataclass(frozen=True)
class DomainResult:
    domain: str
    accepted: bool
    answered_resolvers: int
    cn_resolvers: int
    public_ips: int
    cn_ips: int


@dataclass(frozen=True)
class ExclusionRules:
    suffixes: frozenset[str]
    keywords: frozenset[str]


def normalize_domain(value: str, allow_tld: bool = False) -> str | None:
    domain = value.strip().lower().rstrip(".")
    if domain.startswith("*."):
        domain = domain[2:]
    if domain.startswith("+."):
        domain = domain[2:]
    if domain.startswith("."):
        domain = domain[1:]
    if not domain or "/" in domain or "*" in domain:
        return None
    if not allow_tld and "." not in domain:
        return None
    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        return None
    if not VALID_DOMAIN_RE.match(domain) or ".." in domain:
        return None
    return domain


def mmdb_path_from_args(args: argparse.Namespace) -> Path:
    if args.database:
        return Path(args.database)
    data = fetch_bytes(args.mmdb_url, token=None)
    tmp = tempfile.NamedTemporaryFile(prefix="country-", suffix=".mmdb", delete=False)
    with tmp:
        tmp.write(data)
    return Path(tmp.name)


def geosite_path_from_args(args: argparse.Namespace) -> Path:
    if args.geosite:
        return Path(args.geosite)
    data = fetch_bytes(args.geosite_url, token=None)
    tmp = tempfile.NamedTemporaryFile(prefix="geosite-", suffix=".dat", delete=False)
    with tmp:
        tmp.write(data)
    return Path(tmp.name)


def parse_arrs_domains(path: Path) -> ExclusionRules:
    suffixes: set[str] = set()
    keywords: set[str] = set()
    if not path.exists():
        return ExclusionRules(frozenset(), frozenset())
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("name") or line.startswith("routing"):
            continue
        parts = [part.strip() for part in line.split(",", 1)]
        if len(parts) != 2:
            continue
        rule_type, value = parts
        domain = normalize_domain(value, allow_tld=True)
        if domain is None:
            continue
        if rule_type == "3":
            keywords.add(domain)
        else:
            suffixes.add(domain)
    return ExclusionRules(frozenset(suffixes), frozenset(keywords))


def geosite_exclusions(geosite_path: Path, code: str) -> ExclusionRules:
    rules, _unsupported, _source_count = extract_geosite_rules(geosite_path, code)
    suffixes: set[str] = set()
    keywords: set[str] = set()
    for rule_type, value in rules:
        domain = normalize_domain(value)
        if domain is None:
            continue
        if rule_type == 3:
            keywords.add(domain)
        else:
            suffixes.add(domain)
    return ExclusionRules(frozenset(suffixes), frozenset(keywords))


def combine_exclusions(items: Iterable[ExclusionRules]) -> ExclusionRules:
    suffixes: set[str] = set()
    keywords: set[str] = set()
    for item in items:
        suffixes.update(item.suffixes)
        keywords.update(item.keywords)
    return ExclusionRules(frozenset(suffixes), frozenset(keywords))


def anywhere_rules_db_path_from_args(args: argparse.Namespace) -> Path | None:
    if args.anywhere_rules_db:
        return Path(args.anywhere_rules_db)
    if not args.anywhere_rules_db_url:
        return None
    data = fetch_bytes(args.anywhere_rules_db_url, token=None)
    tmp = tempfile.NamedTemporaryFile(prefix="anywhere-rules-", suffix=".db", delete=False)
    with tmp:
        tmp.write(data)
    return Path(tmp.name)


def anywhere_cn_exclusions(database_path: Path | None, source: str) -> ExclusionRules:
    if database_path is None or not database_path.exists():
        return ExclusionRules(frozenset(), frozenset())

    suffixes: set[str] = set()
    keywords: set[str] = set()
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT type, value FROM rules WHERE source = ? AND type IN (2, 3)",
            (source,),
        )
        for rule_type, value in rows:
            if not isinstance(value, str):
                continue
            domain = normalize_domain(value, allow_tld=True)
            if domain is None:
                continue
            if int(rule_type) == 3:
                keywords.add(domain)
            else:
                suffixes.add(domain)
    return ExclusionRules(frozenset(suffixes), frozenset(keywords))


def is_excluded(domain: str, exclusions: ExclusionRules) -> bool:
    labels = domain.split(".")
    for index in range(len(labels)):
        suffix = ".".join(labels[index:])
        if suffix in exclusions.suffixes:
            return True
    return any(keyword in domain for keyword in exclusions.keywords)


def is_public_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def is_cn_ip(reader: maxminddb.Reader, value: str) -> bool:
    data = reader.get(value)
    if not isinstance(data, dict):
        return False
    country = data.get("country")
    return isinstance(country, dict) and country.get("iso_code") == "CN"


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def fetch_accelerated_domains(url: str, limit: int | None = None) -> list[str]:
    text = fetch_bytes(url, token=None).decode("utf-8-sig", errors="replace")
    domains: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = DNSMASQ_DOMAIN_RE.match(line)
        if not match:
            continue
        domain = normalize_domain(match.group(1), allow_tld=True)
        if domain is None or domain in seen:
            continue
        seen.add(domain)
        domains.append(domain)
        if limit is not None and len(domains) >= limit:
            break
    return domains


def query_doh_persistent(domain: str, endpoint: str, timeout: float, record_types: list[str]) -> list[str]:
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc:
        return []
    connections = getattr(THREAD_STATE, "connections", None)
    if connections is None:
        connections = {}
        THREAD_STATE.connections = connections

    ips: list[str] = []
    for record_type in record_types:
        query = urlencode({"name": domain, "type": record_type})
        target = f"{parsed.path or '/'}?{query}"
        key = (parsed.netloc, timeout)
        connection = connections.get(key)
        if connection is None:
            connection = http.client.HTTPSConnection(parsed.netloc, timeout=timeout)
            connections[key] = connection
        try:
            connection.request(
                "GET",
                target,
                headers={
                    "Accept": "application/dns-json",
                    "Connection": "keep-alive",
                    "User-Agent": "anywhere-rules-cn-accelerated",
                },
            )
            response = connection.getresponse()
            payload = response.read()
            if response.status != 200:
                continue
            data = json.loads(payload.decode("utf-8"))
        except Exception:
            try:
                connection.close()
            except Exception:
                pass
            connections.pop(key, None)
            continue
        for answer in data.get("Answer", []):
            if not isinstance(answer, dict):
                continue
            value = answer.get("data")
            if isinstance(value, str):
                ips.append(value)
    return ips


def evaluate_domain_with_doh(
    domain: str,
    endpoints: list[str],
    timeout: float,
    record_types: list[str],
    reader: maxminddb.Reader,
    min_resolvers: int,
    min_cn_resolvers: int,
    min_cn_ratio: float,
) -> DomainResult:
    answered_resolvers = 0
    cn_resolvers = 0
    public_ips = 0
    cn_ips = 0

    for endpoint in endpoints:
        ips = [
            ip
            for ip in query_doh_persistent(domain, endpoint, timeout, record_types)
            if is_public_ip(ip)
        ]
        if not ips:
            continue
        answered_resolvers += 1
        resolver_cn_ips = sum(1 for ip in ips if is_cn_ip(reader, ip))
        public_ips += len(ips)
        cn_ips += resolver_cn_ips
        if resolver_cn_ips == len(ips):
            cn_resolvers += 1

    ratio = (cn_ips / public_ips) if public_ips else 0.0
    accepted = (
        answered_resolvers >= min_resolvers
        and cn_resolvers >= min_cn_resolvers
        and ratio >= min_cn_ratio
    )
    return DomainResult(domain, accepted, answered_resolvers, cn_resolvers, public_ips, cn_ips)


def write_rule_file(output: Path, rules: list[str], stats: dict[str, int | float | str]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    body = [
        "# NAME: CN_Accelerated",
        "# GENERATED-FOR: Anywhere Routing Rule Set",
        "# DESCRIPTION: 中国大陆 DNS 加速域名补充",
        f"# RULES: {len(rules)}",
        "# SKIPPED: 0",
        f"# CANDIDATES: {stats['candidates']}",
        f"# EXCLUDED: {stats['excluded']}",
        f"# DNS-EVALUATED: {stats['evaluated']}",
        f"# ACCEPTED-BEFORE-EXCLUSION: {stats['accepted_before_exclusion']}",
        f"# MIN-CN-RATIO: {stats['min_cn_ratio']}",
        "# SOURCES:",
        f"# - {stats['source_url']}",
        f"# - {stats['mmdb_url']}",
        f"# - {stats['geosite_url']}",
        f"# - {stats['anywhere_rules_db_url']}",
        "",
        "name = CN_Accelerated",
        "routing = 1",
    ]
    body.extend(f"2, {domain}" for domain in rules)
    output.write_text("\n".join(body) + "\n", encoding="utf-8")


def update_index(output_dir: Path, output: Path, rules: list[str], stats: dict[str, int | float | str]) -> None:
    index_path = output_dir / "index.json"
    if not index_path.exists():
        return
    index = json.loads(index_path.read_text(encoding="utf-8"))
    files = [
        item for item in index.get("files", [])
        if item.get("name") != "CN_Accelerated"
    ]
    files.append(
        {
            "name": "CN_Accelerated",
            "description": "中国大陆 DNS 加速域名补充",
            "output_path": output.relative_to(output_dir.parent).as_posix(),
            "rule_count": len(rules),
            "skipped_count": 0,
            "unsupported_types": {},
            "sources": [
                str(stats["source_url"]),
                str(stats["mmdb_url"]),
                str(stats["geosite_url"]),
                str(stats["anywhere_rules_db_url"]),
            ],
        }
    )
    index["files"] = files
    index["total_files"] = len(files)
    index["total_rules"] = sum(int(item.get("rule_count", 0)) for item in files)
    index["total_skipped"] = sum(int(item.get("skipped_count", 0)) for item in files)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_catalog(output_dir: Path, output: Path, rules: list[str]) -> None:
    catalog_path = output_dir / "catalog.md"
    if not catalog_path.exists():
        return
    lines = [
        line for line in catalog_path.read_text(encoding="utf-8").splitlines()
        if "| CN_Accelerated " not in line
    ]
    output_path = output.relative_to(output_dir.parent).as_posix()
    lines.append(
        f"| CN_Accelerated | {len(rules)} | 0 | 中国大陆 DNS 加速域名补充 | "
        f"[{output_path}](./{output.name}) |"
    )
    catalog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", default="rules")
    parser.add_argument("--limit", type=positive_int, help="Limit candidates for local tests.")
    parser.add_argument("--workers", type=positive_int, default=96)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--record-type", action="append", dest="record_types", choices=("A", "AAAA"))
    parser.add_argument("--min-resolvers", type=positive_int, default=1)
    parser.add_argument("--min-cn-resolvers", type=positive_int, default=1)
    parser.add_argument("--min-cn-ratio", type=float, default=1.0)
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--doh-endpoint", action="append", dest="doh_endpoints")
    parser.add_argument("--database", help="Use a local Country.mmdb instead of downloading mmdb-url.")
    parser.add_argument("--mmdb-url", default=DEFAULT_MMDB_URL)
    parser.add_argument("--geosite", help="Use a local geosite.dat instead of downloading geosite-url.")
    parser.add_argument("--geosite-url", default=DEFAULT_GEOSITE_URL)
    parser.add_argument("--anywhere-rules-db", help="Use a local Anywhere Rules.db for CN exclusions.")
    parser.add_argument("--anywhere-rules-db-url", default=DEFAULT_ANYWHERE_RULES_DB_URL)
    parser.add_argument("--anywhere-cn-source", default="CN")
    parser.add_argument("--no-dns-verify", action="store_true")
    parser.add_argument("--no-update-index", action="store_true")
    args = parser.parse_args()

    if args.min_cn_ratio < 0 or args.min_cn_ratio > 1:
        raise RuntimeError("--min-cn-ratio must be between 0 and 1.")

    output_dir = Path(args.dist) / "common"
    output = output_dir / "CN_Accelerated.arrs"
    record_types = args.record_types or ["A"]
    sources = [("doh", endpoint) for endpoint in (args.doh_endpoints or DEFAULT_DOH_ENDPOINTS)]

    print("Fetching dnsmasq-china-list accelerated domains...", flush=True)
    candidates = fetch_accelerated_domains(args.source_url, args.limit)
    print(f"Loaded {len(candidates)} candidate domains.", flush=True)

    print("Loading exclusion sets...", flush=True)
    geosite_path = geosite_path_from_args(args)
    anywhere_rules_db = anywhere_rules_db_path_from_args(args)
    local_geosite_cn = parse_arrs_domains(output_dir / "Geosite_CN.arrs")
    geolocation_not_cn = geosite_exclusions(geosite_path, "GEOLOCATION-!CN")
    anywhere_cn = anywhere_cn_exclusions(anywhere_rules_db, args.anywhere_cn_source)
    exclusions = combine_exclusions([local_geosite_cn, geolocation_not_cn, anywhere_cn])

    filtered_candidates = [domain for domain in candidates if not is_excluded(domain, exclusions)]
    excluded_count = len(candidates) - len(filtered_candidates)
    print(
        f"Excluded {excluded_count} domains using Geosite_CN, "
        f"geolocation-!cn, and Anywhere {args.anywhere_cn_source}.",
        flush=True,
    )

    accepted: list[str]
    accepted_before_exclusion: int
    if args.no_dns_verify:
        accepted = filtered_candidates
        accepted_before_exclusion = len(accepted)
    else:
        print("Resolving candidates with CN DNS and checking Country.mmdb...", flush=True)
        database_path = mmdb_path_from_args(args)
        accepted = []
        accepted_before_exclusion = 0
        with maxminddb.open_database(str(database_path)) as reader:
            with ThreadPoolExecutor(max_workers=args.workers) as executor:
                futures = {
                    executor.submit(
                        evaluate_domain_with_doh,
                        domain,
                        [value for _source_type, value in sources],
                        args.timeout,
                        record_types,
                        reader,
                        args.min_resolvers,
                        args.min_cn_resolvers,
                        args.min_cn_ratio,
                    ): domain
                    for domain in filtered_candidates
                }
                for index, future in enumerate(as_completed(futures), start=1):
                    result: DomainResult = future.result()
                    if result.accepted:
                        accepted_before_exclusion += 1
                        accepted.append(result.domain)
                    if index % 2000 == 0:
                        print(
                            f"Evaluated {index}/{len(filtered_candidates)} domains, accepted {len(accepted)}.",
                            flush=True,
                        )

    rules = sorted(set(accepted))
    stats: dict[str, int | float | str] = {
        "candidates": len(candidates),
        "excluded": excluded_count,
        "evaluated": len(filtered_candidates),
        "accepted_before_exclusion": accepted_before_exclusion,
        "min_cn_ratio": args.min_cn_ratio,
        "source_url": args.source_url,
        "mmdb_url": args.mmdb_url,
        "geosite_url": args.geosite_url,
        "anywhere_rules_db_url": args.anywhere_rules_db_url,
    }
    write_rule_file(output, rules, stats)
    if not args.no_update_index:
        update_index(output_dir, output, rules, stats)
        update_catalog(output_dir, output, rules)
    print(f"Built {len(rules)} CN accelerated rules at {output}.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
