#!/usr/bin/env python3
"""Build a CN geosite Anywhere rule set from v2ray geosite.dat."""

from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from convert_blackmatrix7 import fetch_bytes


MAX_RULES_PER_SET = 100000
DEFAULT_SOURCE_URL = "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat"
DEFAULT_CODE = "GEOLOCATION-CN"

GEOSITE_TYPE_NAMES = {
    0: "Plain",
    1: "Regex",
    2: "Domain",
    3: "Full",
}


@dataclass
class GeositeRuleSet:
    name: str
    description: str
    output_path: str
    rule_count: int
    skipped_count: int
    unsupported_types: dict[str, int]
    sources: list[str]


def read_varint(data: bytes, offset: int) -> tuple[int, int]:
    shift = 0
    result = 0
    while True:
        value = data[offset]
        offset += 1
        result |= (value & 0x7F) << shift
        if not value & 0x80:
            return result, offset
        shift += 7
        if shift > 63:
            raise ValueError("Invalid varint in geosite.dat.")


def iter_fields(data: bytes) -> Iterator[tuple[int, int, int | bytes]]:
    offset = 0
    while offset < len(data):
        key, offset = read_varint(data, offset)
        field_number = key >> 3
        wire_type = key & 7
        if wire_type == 0:
            value, offset = read_varint(data, offset)
            yield field_number, wire_type, value
        elif wire_type == 1:
            value = data[offset:offset + 8]
            offset += 8
            yield field_number, wire_type, value
        elif wire_type == 2:
            length, offset = read_varint(data, offset)
            value = data[offset:offset + length]
            offset += length
            yield field_number, wire_type, value
        elif wire_type == 5:
            value = data[offset:offset + 4]
            offset += 4
            yield field_number, wire_type, value
        else:
            raise ValueError(f"Unsupported protobuf wire type: {wire_type}")


def parse_domain(data: bytes) -> tuple[int | None, str | None]:
    domain_type: int | None = None
    value: str | None = None
    for field_number, wire_type, field_value in iter_fields(data):
        if field_number == 1 and wire_type == 0 and isinstance(field_value, int):
            domain_type = field_value
        elif field_number == 2 and wire_type == 2 and isinstance(field_value, bytes):
            value = field_value.decode("utf-8", errors="replace").strip()
    return domain_type, value


def parse_site(data: bytes) -> tuple[str | None, list[tuple[int | None, str | None]]]:
    code: str | None = None
    domains: list[tuple[int | None, str | None]] = []
    for field_number, wire_type, field_value in iter_fields(data):
        if field_number == 1 and wire_type == 2 and isinstance(field_value, bytes):
            code = field_value.decode("utf-8", errors="replace")
        elif field_number == 2 and wire_type == 2 and isinstance(field_value, bytes):
            domains.append(parse_domain(field_value))
    return code, domains


def extract_rules(
    geosite_path: Path,
    code: str,
) -> tuple[list[tuple[int, str]], dict[str, int], int]:
    wanted = code.upper()
    rules: set[tuple[int, str]] = set()
    unsupported: dict[str, int] = {}
    source_count = 0

    for field_number, wire_type, field_value in iter_fields(geosite_path.read_bytes()):
        if field_number != 1 or wire_type != 2 or not isinstance(field_value, bytes):
            continue
        site_code, domains = parse_site(field_value)
        if site_code is None or site_code.upper() != wanted:
            continue
        source_count = len(domains)
        for domain_type, value in domains:
            if not value:
                unsupported["Empty"] = unsupported.get("Empty", 0) + 1
                continue
            if domain_type == 0:
                rules.add((3, value))
            elif domain_type in {2, 3}:
                rules.add((2, value))
            else:
                type_name = GEOSITE_TYPE_NAMES.get(domain_type, f"Unknown({domain_type})")
                unsupported[type_name] = unsupported.get(type_name, 0) + 1
        break

    if source_count == 0:
        raise RuntimeError(f"Geosite code not found or empty: {code}")

    return sorted(rules, key=lambda item: (item[0], item[1])), unsupported, source_count


def write_rule_file(
    output: Path,
    name: str,
    description: str,
    rules: list[tuple[int, str]],
    source_url: str,
    geosite_code: str,
    source_count: int,
    unsupported: dict[str, int],
    total_rules: int | None = None,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    skipped_count = sum(unsupported.values())
    body = [
        f"# NAME: {name}",
        "# GENERATED-FOR: Anywhere Routing Rule Set",
        f"# DESCRIPTION: {description}",
        f"# GEOSITE-CODE: {geosite_code}",
        f"# RULES: {len(rules)}",
        f"# SOURCE-RULES: {source_count}",
        f"# SKIPPED: {skipped_count}",
    ]
    if total_rules is not None and total_rules != len(rules):
        body.append(f"# OUTPUT-SOURCE-RULES: {total_rules}")
    if unsupported:
        summary = ", ".join(f"{key}={unsupported[key]}" for key in sorted(unsupported))
        body.append(f"# SKIPPED-TYPES: {summary}")
    body.extend([
        "# SOURCES:",
        f"# - {source_url}",
        "",
        f"name = {name}",
    ])
    body.extend(f"{rule_type}, {value}" for rule_type, value in rules)
    output.write_text("\n".join(body) + "\n", encoding="utf-8")


def build_outputs(
    output_dir: Path,
    rules: list[tuple[int, str]],
    unsupported: dict[str, int],
    source_url: str,
    geosite_code: str,
    source_count: int,
) -> list[GeositeRuleSet]:
    for stale in output_dir.glob("Geosite_CN*.arrs"):
        stale.unlink()

    description = "Geosite 中国大陆域名规则"
    if len(rules) <= MAX_RULES_PER_SET:
        name = "Geosite_CN"
        output = output_dir / f"{name}.arrs"
        write_rule_file(output, name, description, rules, source_url, geosite_code, source_count, unsupported)
        return [
            GeositeRuleSet(
                name=name,
                description=description,
                output_path=output.relative_to(output_dir.parent).as_posix(),
                rule_count=len(rules),
                skipped_count=sum(unsupported.values()),
                unsupported_types=unsupported,
                sources=[source_url],
            )
        ]

    chunks = [
        rules[index:index + MAX_RULES_PER_SET]
        for index in range(0, len(rules), MAX_RULES_PER_SET)
    ]
    built: list[GeositeRuleSet] = []
    for index, chunk in enumerate(chunks, start=1):
        name = f"Geosite_CN_{index:02d}"
        part_description = f"{description}（分片 {index}/{len(chunks)}）"
        output = output_dir / f"{name}.arrs"
        part_unsupported = unsupported if index == 1 else {}
        write_rule_file(
            output,
            name,
            part_description,
            chunk,
            source_url,
            geosite_code,
            source_count,
            part_unsupported,
            total_rules=len(rules),
        )
        built.append(
            GeositeRuleSet(
                name=name,
                description=part_description,
                output_path=output.relative_to(output_dir.parent).as_posix(),
                rule_count=len(chunk),
                skipped_count=sum(part_unsupported.values()),
                unsupported_types=part_unsupported,
                sources=[source_url],
            )
        )
    return built


def update_index(output_dir: Path, built: list[GeositeRuleSet]) -> None:
    index_path = output_dir / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    files = [
        item for item in index.get("files", [])
        if not str(item.get("name", "")).startswith("Geosite_CN")
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


def update_catalog(output_dir: Path, built: list[GeositeRuleSet]) -> None:
    catalog_path = output_dir / "catalog.md"
    lines = catalog_path.read_text(encoding="utf-8").splitlines()
    lines = [
        line for line in lines
        if "| Geosite_CN" not in line
    ]
    for item in built:
        description = item.description.replace("|", "\\|")
        lines.append(
            f"| {item.name} | {item.rule_count} | {item.skipped_count} | "
            f"{description} | [{item.output_path}](./{Path(item.output_path).name}) |"
        )
    catalog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def geosite_path_from_args(args: argparse.Namespace) -> Path:
    if args.geosite:
        return Path(args.geosite)
    data = fetch_bytes(args.source_url, token=None)
    tmp = tempfile.NamedTemporaryFile(prefix="geosite-", suffix=".dat", delete=False)
    with tmp:
        tmp.write(data)
    return Path(tmp.name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", default="rules")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--geosite-code", default=DEFAULT_CODE)
    parser.add_argument("--geosite", help="Use a local geosite.dat instead of downloading source-url.")
    args = parser.parse_args()

    output_dir = Path(args.dist) / "common"
    geosite_path = geosite_path_from_args(args)
    rules, unsupported, source_count = extract_rules(geosite_path, args.geosite_code)
    built = build_outputs(output_dir, rules, unsupported, args.source_url, args.geosite_code, source_count)
    update_index(output_dir, built)
    update_catalog(output_dir, built)
    skipped = sum(item.skipped_count for item in built)
    print(
        f"Built {sum(item.rule_count for item in built)} Geosite CN rules "
        f"in {len(built)} file(s), skipped {skipped} entries."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
