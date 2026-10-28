#!/usr/bin/env python3
"""Flag stale, incomplete or stuck deals in a CRM CSV export."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

ALIASES = {
    "deal_id": ["deal_id", "id", "opportunity id"],
    "name": ["name", "deal name", "opportunity", "opportunity name"],
    "stage": ["stage", "deal stage"],
    "amount": ["amount", "value", "deal value"],
    "close_date": ["close_date", "close date", "expected close", "expected close date"],
    "last_activity": ["last_activity", "last activity", "last activity date"],
    "next_step": ["next_step", "next step"],
    "stage_entered": ["stage_entered", "stage entered", "stage entered date"],
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


def parse_date(value):
    text = (value or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(value):
    text = (value or "").replace(",", "").replace("$", "").replace("EUR", "").strip()
    try:
        return float(text)
    except ValueError:
        return 0.0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="CRM deal export CSV")
    parser.add_argument("--out", help="flagged CSV path")
    parser.add_argument("--report", help="JSON report path")
    parser.add_argument("--stale-days", type=int, default=30)
    parser.add_argument("--stuck-days", type=int, default=45)
    parser.add_argument("--today", help="YYYY-MM-DD, defaults to today")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"input not found: {path}", file=sys.stderr)
        return 2
    today = parse_date(args.today) if args.today else dt.date.today()
    if today is None:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        mapping = build_map(fieldnames)
        missing = [k for k in ("name", "amount") if k not in mapping]
        if missing:
            print("missing required column(s): " + ", ".join(missing), file=sys.stderr)
            return 2
        rows = list(reader)

    flags = {"missing_close_date": [], "missing_next_step": [], "stale": [], "stuck": []}
    total_value = 0.0
    flagged_value = 0.0
    flagged = 0
    out_rows = []
    for row in rows:
        amount = parse_amount(row.get(mapping.get("amount", ""), ""))
        total_value += amount
        row_flags = []
        close = parse_date(row.get(mapping.get("close_date", ""), ""))
        if close is None:
            row_flags.append("missing_close_date")
        next_step = (row.get(mapping.get("next_step", ""), "") or "").strip()
        if not next_step or next_step.lower() in {"follow up", "follow-up", "tbd"}:
            row_flags.append("missing_next_step")
        last = parse_date(row.get(mapping.get("last_activity", ""), ""))
        if last is not None and (today - last).days > args.stale_days:
            row_flags.append("stale")
        entered = parse_date(row.get(mapping.get("stage_entered", ""), ""))
        if entered is not None and (today - entered).days > args.stuck_days:
            row_flags.append("stuck")
        if row_flags:
            flagged += 1
            flagged_value += amount
            for flag in row_flags:
                flags[flag].append(row)
        out_row = dict(row)
        out_row["flags"] = ";".join(row_flags)
        out_rows.append(out_row)

    out_path = Path(args.out) if args.out else path.with_name(path.stem + ".flagged.csv")
    names = fieldnames + ["flags"]
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        writer.writerows(out_rows)

    by_flag = {}
    for flag, items in flags.items():
        by_flag[flag] = {"deals": len(items), "value": round(sum(parse_amount(r.get(mapping.get("amount", ""), "")) for r in items), 2)}

    report = {
        "deals": len(rows),
        "flagged": flagged,
        "total_value": round(total_value, 2),
        "flagged_value": round(flagged_value, 2),
        "by_flag": by_flag,
        "thresholds": {"stale_days": args.stale_days, "stuck_days": args.stuck_days},
    }
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Deals: {len(rows)}, flagged: {flagged}, value flagged: {flagged_value:,.0f}")
    for flag, data in by_flag.items():
        print(f"- {flag}: {data['deals']} deals, {data['value']:,.0f}")
    print(f"flagged CSV: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
