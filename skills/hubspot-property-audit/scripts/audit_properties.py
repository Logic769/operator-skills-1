#!/usr/bin/env python3
"""Audit a HubSpot property export for duplicate labels, missing docs and picklist drift."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ALIASES = {
    "name": ["name", "internal name", "property name"],
    "label": ["label", "display label"],
    "group": ["group", "group name"],
    "description": ["description"],
    "options": ["options", "choices"],
    "type": ["type", "field type"],
}


def build_map(fieldnames):
    lower = {f.strip().lower(): f for f in fieldnames if f}
    mapping = {}
    for key, names in ALIASES.items():
        for name in names:
            if name in lower:
                mapping[key] = lower[name]
                break
    return mapping


def split_options(value):
    text = (value or "").strip()
    if not text:
        return []
    parts = [p.strip() for p in text.replace("|", ";").split(";")]
    return [p for p in parts if p]


def load_usage(path):
    usage = {}
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        names = {f.strip().lower(): f for f in (reader.fieldnames or []) if f}
        prop_col = names.get("property") or names.get("property name") or names.get("internal name")
        count_col = names.get("count") or names.get("usage")
        if not prop_col or not count_col:
            raise ValueError("usage CSV needs property and count columns")
        for row in reader:
            try:
                usage[row[prop_col].strip()] = int(float(row[count_col]))
            except (TypeError, ValueError):
                continue
    return usage


def audit(rows, mapping, usage):
    findings = defaultdict(list)
    by_label = defaultdict(list)
    group_options = defaultdict(lambda: defaultdict(list))
    for row in rows:
        name = (row.get(mapping.get("name", ""), "") or "").strip()
        label = (row.get(mapping.get("label", ""), "") or "").strip()
        group = (row.get(mapping.get("group", ""), "") or "").strip()
        description = (row.get(mapping.get("description", ""), "") or "").strip()
        options = split_options(row.get(mapping.get("options", ""), ""))
        if label:
            by_label[label.lower()].append(name)
        if not description:
            findings["missing_description"].append(name)
        if usage is not None and usage.get(name, 0) == 0:
            findings["unused"].append(name)
        if options:
            normalised = tuple(options)
            group_options[group or "(no group)"][normalised].append(name)
            if len(set(o.lower() for o in options)) != len(options):
                findings["inconsistent_picklist"].append(name)
    duplicate_groups = []
    for label, names in by_label.items():
        if len(names) > 1:
            duplicate_groups.append({"label": label, "properties": names})
            findings["duplicate_label"].extend(names)
    picklist_groups = []
    for group, variants in group_options.items():
        if len(variants) > 1:
            picklist_groups.append({"group": group, "variants": [list(v) for v in variants]})
            for names in variants.values():
                findings["inconsistent_picklist"].extend(names)
    return findings, duplicate_groups, picklist_groups


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="HubSpot property export CSV")
    parser.add_argument("--usage", help="optional property usage CSV")
    parser.add_argument("--out", help="flagged CSV path")
    parser.add_argument("--report", help="JSON report path")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"input not found: {path}", file=sys.stderr)
        return 2
    usage = None
    if args.usage:
        try:
            usage = load_usage(args.usage)
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        mapping = build_map(fieldnames)
        if "name" not in mapping or "label" not in mapping:
            print("missing required column(s): name and label", file=sys.stderr)
            return 2
        rows = list(reader)

    findings, duplicate_groups, picklist_groups = audit(rows, mapping, usage)
    flagged = set()
    out_rows = []
    for row in rows:
        name = (row.get(mapping["name"], "") or "").strip()
        tags = [key for key, names in findings.items() if name in names]
        if tags:
            flagged.add(name)
        out_row = dict(row)
        out_row["findings"] = ";".join(sorted(set(tags)))
        out_rows.append(out_row)

    out_path = Path(args.out) if args.out else path.with_name(path.stem + ".audited.csv")
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames + ["findings"])
        writer.writeheader()
        writer.writerows(out_rows)

    report = {
        "properties": len(rows),
        "flagged": len(flagged),
        "by_finding": {key: len(sorted(set(names))) for key, names in findings.items()},
        "duplicate_labels": duplicate_groups,
        "picklist_drift": picklist_groups,
        "usage_supplied": usage is not None,
    }
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Properties: {len(rows)}, flagged: {len(flagged)}")
    for key, count in report["by_finding"].items():
        print(f"- {key}: {count}")
    if usage is None:
        print("- unused: unknown (no usage export supplied)")
    print(f"flagged CSV: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
