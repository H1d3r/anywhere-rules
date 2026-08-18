#!/usr/bin/env python3
"""Build a CN GeoIP Anywhere rule set from a MaxMind mmdb database."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import maxminddb

from convert_blackmatrix7 import fetch_bytes


MAX_RULES_PER_SET = 100000
DEFAULT_SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb"
ICON_HEADER_RE = re.compile(r"^icon-(?:light|dark)\s*=\s*\S+\s*$")


@dataclass
class GeoIPRuleSet:
    name: str
    description: str
    output_path: str
    rule_count: int
    skipped_count: int
    unsupported_types: dict[str, int]
    sources: list[str]


def read_icon_headers(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if ICON_HEADER_RE.fullmatch(line.strip())
    ]


def country_code(data: dict[str, object]) -> str | None:
    country = data.get("country")
    if isinstance(country, dict):
        value = country.get("iso_code")
        if isinstance(value, str):
            return value
    return None


def extract_cn_rules(database_path: Path) -> list[tuple[int, str]]:
    rules: list[tuple[int, str]] = []
    with maxminddb.open_database(str(database_path)) as reader:
        for network, data in reader:
            if not isinstance(data, dict) or country_code(data) != "CN":
                continue
            rule_type = 0 if network.version == 4 else 1
            rules.append((rule_type, str(network)))
    return sorted(rules, key=lambda item: (item[0], item[1]))


def write_rule_file(
    output: Path,
    name: str,
    description: str,
    rules: list[tuple[int, str]],
    source_url: str,
    total_rules: int | None = None,
    icon_headers: list[str] | None = None,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if icon_headers is None:
        icon_headers = read_icon_headers(output)
    body = [
        f"# NAME: {name}",
        "# GENERATED-FOR: Anywhere Routing Rule Set",
        f"# DESCRIPTION: {description}",
        f"# RULES: {len(rules)}",
        "# SKIPPED: 0",
    ]
    if total_rules is not None and total_rules != len(rules):
        body.append(f"# SOURCE-RULES: {total_rules}")
    body.extend([
        "# SOURCES:",
        f"# - {source_url}",
        "",
        f"name = {name}",
        *icon_headers,
        "routing = 1",
    ])
    body.extend(f"{rule_type}, {value}" for rule_type, value in rules)
    output.write_text("\n".join(body) + "\n", encoding="utf-8")


def build_outputs(
    output_dir: Path,
    rules: list[tuple[int, str]],
    source_url: str,
) -> list[GeoIPRuleSet]:
    preserved_icons = {
        stale.name: read_icon_headers(stale)
        for stale in output_dir.glob("GeoIP_CN*.arrs")
        if stale.is_file()
    }
    for stale in output_dir.glob("GeoIP_CN*.arrs"):
        stale.unlink()

    description = "GeoIP 中国大陆 IP CIDR"
    if len(rules) <= MAX_RULES_PER_SET:
        name = "GeoIP_CN"
        output = output_dir / f"{name}.arrs"
        write_rule_file(
            output,
            name,
            description,
            rules,
            source_url,
            icon_headers=preserved_icons.get(output.name),
        )
        return [
            GeoIPRuleSet(
                name=name,
                description=description,
                output_path=output.relative_to(output_dir.parent).as_posix(),
                rule_count=len(rules),
                skipped_count=0,
                unsupported_types={},
                sources=[source_url],
            )
        ]

    chunks = [
        rules[index:index + MAX_RULES_PER_SET]
        for index in range(0, len(rules), MAX_RULES_PER_SET)
    ]
    built: list[GeoIPRuleSet] = []
    for index, chunk in enumerate(chunks, start=1):
        name = f"GeoIP_CN_{index:02d}"
        part_description = f"{description}（分片 {index}/{len(chunks)}）"
        output = output_dir / f"{name}.arrs"
        write_rule_file(
            output,
            name,
            part_description,
            chunk,
            source_url,
            total_rules=len(rules),
            icon_headers=preserved_icons.get(output.name),
        )
        built.append(
            GeoIPRuleSet(
                name=name,
                description=part_description,
                output_path=output.relative_to(output_dir.parent).as_posix(),
                rule_count=len(chunk),
                skipped_count=0,
                unsupported_types={},
                sources=[source_url],
            )
        )
    return built


def update_index(output_dir: Path, built: list[GeoIPRuleSet]) -> None:
    index_path = output_dir / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    files = [
        item for item in index.get("files", [])
        if not str(item.get("name", "")).startswith("GeoIP_CN")
    ]
    files.extend(
        {
            "name": item.name,
            "description": item.description,
            "output_path": item.output_path,
            "rule_count": item.rule_count,
            "skipped_count": item.skipped_count,
            "unsupported_types": item.unsupported_types,
            "sources": item.sources,
        }
        for item in built
    )
    index["files"] = files
    index["total_files"] = len(files)
    index["total_rules"] = sum(int(item.get("rule_count", 0)) for item in files)
    index["total_skipped"] = sum(int(item.get("skipped_count", 0)) for item in files)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_catalog(output_dir: Path, built: list[GeoIPRuleSet]) -> None:
    catalog_path = output_dir / "catalog.md"
    lines = catalog_path.read_text(encoding="utf-8").splitlines()
    lines = [
        line for line in lines
        if "| GeoIP_CN" not in line
    ]
    for item in built:
        description = item.description.replace("|", "\\|")
        lines.append(
            f"| {item.name} | {item.rule_count} | {item.skipped_count} | "
            f"{description} | [{item.output_path}](./{Path(item.output_path).name}) |"
        )
    catalog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def database_path_from_args(args: argparse.Namespace) -> Path:
    if args.database:
        return Path(args.database)
    data = fetch_bytes(args.source_url, token=None)
    tmp = tempfile.NamedTemporaryFile(prefix="country-", suffix=".mmdb", delete=False)
    with tmp:
        tmp.write(data)
    return Path(tmp.name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", default="rules")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--database", help="Use a local mmdb instead of downloading source-url.")
    args = parser.parse_args()

    output_dir = Path(args.dist) / "common"
    database_path = database_path_from_args(args)
    rules = extract_cn_rules(database_path)
    built = build_outputs(output_dir, rules, args.source_url)
    update_index(output_dir, built)
    update_catalog(output_dir, built)
    print(f"Built {sum(item.rule_count for item in built)} GeoIP CN rules in {len(built)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
