from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Tuple

from src.common.models import OrderEvent

DDL = """
CREATE TABLE orders_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT,
    event_ts TIMESTAMPTZ,
    order_id TEXT,
    customer_id TEXT,
    status TEXT,
    amount NUMERIC,
    currency TEXT,
    items_count INT
);
"""

def validate_event(payload: dict) -> OrderEvent:
    """Validate a single event against the OrderEvent schema."""
    return OrderEvent(**payload)


def validate_file(path: Path) -> Tuple[int, int]:
    """Validate all JSONL events in a file. Returns (ok_count, err_count)."""
    ok, err = 0, 0
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                _ = validate_event(payload)
                ok += 1
            except Exception as e:
                err += 1
                print(f"[line {i}] invalid event: {e}")
    return ok, err


def main():
    parser = argparse.ArgumentParser(
        description="Validate JSONL order events from a file."
    )
    parser.add_argument(
        "--file",
        type=str,
        default="data/orders_log.jsonl",
        help="Path to a JSONL file of events (default: data/orders_log.jsonl)",
    )
    parser.add_argument(
        "--show-schema",
        action="store_true",
        help="Print the SQL schema for the orders_events table",
    )
    args = parser.parse_args()

    if args.show_schema:
        print(DDL.strip())
        raise SystemExit(0)

    path = Path(args.file)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    ok, err = validate_file(path)
    print(f"✅ {ok} events valid | ❌ {err} errors")


if __name__ == "__main__":
    main()
