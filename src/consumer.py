from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Tuple

from src.common.models import OrderEvent


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
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}")
        raise SystemExit(1)

    ok, err = validate_file(path)
    print(f"Validation summary → OK: {ok}, ERRORS: {err}")


if __name__ == "__main__":
    main()
