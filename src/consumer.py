from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from decimal import Decimal 
import psycopg2
import csv
import logging

from src.common.models import OrderEvent
from collections import Counter
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Postgres Configuration
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_DB = os.getenv("PG_DB", "postgres")

DDL = """
CREATE TABLE IF NOT EXISTS orders_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    event_ts TIMESTAMPTZ NOT NULL,
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    status TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    currency TEXT NOT NULL,
    items_count INT NOT NULL
);
"""

UPSERT = """
INSERT INTO orders_events (
    event_id, event_type, event_ts, order_id, customer_id, status, amount, currency, items_count
) VALUES (
    %(event_id)s, %(event_type)s, %(event_ts)s, %(order_id)s, %(customer_id)s, %(status)s, %(amount)s, %(currency)s, %(items_count)s
)
ON CONFLICT (event_id) DO NOTHING;
"""


def pg_connect():
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASSWORD, dbname=PG_DB
    )


def ensure_db(conn) -> None:
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(DDL)


def validate_event(payload: dict) -> OrderEvent:
    return OrderEvent(**payload)


def _to_db_dict(evt: OrderEvent) -> dict:
    d = evt.model_dump()
    if isinstance(d.get("amount"), str):
        d["amount"] = Decimal(d["amount"])
    return d

from collections import defaultdict
group_totals: dict[str, Decimal] = defaultdict(Decimal)

def validate_file(path: Path, to_postgres: bool = False, to_csv: bool = False, group_by: str | None = None, status_filter: Optional[set[str]] = None, currency_filter: Optional[set[str]] = None, limit: int | None = None,check_duplicates: bool = False,min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,) -> tuple[int, int, Decimal, Counter, Counter,int | None, int | None, int]:
    """Validate all JSONL events"""
    ok, err = 0, 0
    total = Decimal("0")
    status_counts = Counter()
    type_counts = Counter()
    rows: list[dict] = []
    conn = None
    cur = None
    min_amt: Decimal | None = None
    max_amt: Decimal | None = None
    seen_ids: set[str] = set()
    duplicates: int = 0

    try:
        if to_postgres:
            conn = pg_connect()
            ensure_db(conn)
            cur = conn.cursor()

        with path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                if limit and ok >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    evt = validate_event(payload)
                    if check_duplicates:
                        if evt.event_id in seen_ids:
                            duplicates += 1
                            logging.warning(f"⚠️ Duplicate event_id found: {evt.event_id} (line {i})")
                        else:
                            seen_ids.add(evt.event_id)
                    if status_filter and evt.status not in status_filter:
                        continue
                    ok += 1
                    # sum amounts 
                    amt = evt.amount if isinstance(evt.amount, Decimal) else Decimal(str(evt.amount))
                    total += amt
                    # group totals by chosen field
                    if group_by == "category":
                        group_key = getattr(evt, "category", None)
                        if group_key:
                            group_totals[group_key] += amt
                    # new lines for min/max
                    if min_amt is None or amt < min_amt:
                        min_amt = amt
                    if max_amt is None or amt > max_amt:
                        max_amt = amt
                    if min_amount is not None and amt < min_amount:
                        continue
                    if max_amount is not None and amt > max_amount:
                        continue

                    status_counts[evt.status] += 1
                    type_counts[evt.event_type] += 1
                    d = evt.model_dump()
                    if isinstance(d.get("amount"), Decimal):
                        d["amount"] = str(d["amount"])
                    rows.append(d)
                    if to_postgres:
                        cur.execute(UPSERT, _to_db_dict(evt))
                except Exception as e:
                    err += 1
                    logging.error(f"[line {i}] invalid event: {e}")
                if i % 100 == 0:
                    logging.info(f"Processed {i} lines so far → valid: {ok}, errors: {err}")
                if currency_filter and evt.currency.upper() not in currency_filter:
                    continue

        if to_postgres and conn:
            conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    if to_csv:
        out = Path("data/validated_orders.csv")
        out.parent.mkdir(parents=True, exist_ok=True)
        if rows:
            fieldnames = list(rows[0].keys())
            with out.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)

    return ok, err, total, status_counts, type_counts, min_amt, max_amt, duplicates, group_totals

def main():
    parser = argparse.ArgumentParser(description="Validate JSONL order events from a file.")
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
    parser.add_argument(
        "--to-postgres",
        action="store_true",
        help="If set, insert valid events into Postgres after validation",
    )
    parser.add_argument(
    "--to-csv",
    action="store_true",
    help="If set, export valid events to data/validated_orders.csv",
    )
    parser.add_argument(
    "--status",
    type=str,
    help="Comma-separated statuses to include (e.g. DELIVERED,SHIPPED). "
         "Allowed: PLACED,CONFIRMED,SHIPPED,DELIVERED,CANCELLED",
   )
    parser.add_argument(
    "--limit",
    type=int,
    help="Validate only the first N events from the log file",
    )
    parser.add_argument(
    "--summary",
    action="store_true",
    help="If set, export a JSON summary report with totals and counts"
    )
    parser.add_argument(
    "--summary-csv",
    action="store_true",
    help="If set, export a CSV summary report with totals and counts"
    )
    parser.add_argument(
    "--currency",
    type=str,
    help="Comma-separated currencies to include (e.g. USD,EUR,INR)"
    )
    parser.add_argument(
    "--check-duplicates",
    action="store_true",
    help="If set, warn when duplicate event_ids are found"
    )
    parser.add_argument(
    "--min-amount",
    type=float,
    help="Only include events with amount >= this value"
    )
    parser.add_argument(
    "--max-amount",
    type=float,
    help="Only include events with amount <= this value"
    )
    parser.add_argument(
    "--group-by",
    type=str,
    help="Group totals by the given field"
    )

    args = parser.parse_args()

    currency_filter: set[str] | None = None
    if args.currency:
        chosen = {c.strip().upper() for c in args.currency.split(",") if c.strip()}
        currency_filter = chosen

    min_amount: Decimal | None = Decimal(str(args.min_amount)) if args.min_amount is not None else None
    max_amount: Decimal | None = Decimal(str(args.max_amount)) if args.max_amount is not None else None

    allowed_statuses = {"PLACED","CONFIRMED","SHIPPED","DELIVERED","CANCELLED"}
    status_filter: set[str] | None = None
    if args.status:
        chosen = {s.strip().upper() for s in args.status.split(",") if s.strip()}
        invalid = chosen - allowed_statuses
        if invalid:
            raise ValueError(f"Invalid statuses: {sorted(invalid)}. Allowed: {sorted(allowed_statuses)}")
        status_filter = chosen

    if args.show_schema:
        print(DDL.strip())
        raise SystemExit(0)

    path = Path(args.file)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    ok, err, total, status_counts, type_counts, min_amt, max_amt, duplicates, group_totals = validate_file(
    path, to_postgres=args.to_postgres, to_csv=args.to_csv, status_filter=status_filter, limit=args.limit, check_duplicates=args.check_duplicates,min_amount=min_amount,
    max_amount=max_amount, group_by=args.group_by,
    )
    avg = (total / ok).quantize(Decimal("0.01")) if ok else Decimal("0.00")
    label = f" (status in {','.join(sorted(status_filter))})" if status_filter else ""
    logging.info(f"{ok} events valid | {err} errors | total: {total} | avg: {avg}{label}")
    if status_counts:
        logging.info("Status counts → " + " | ".join(f"{k}: {v}" for k, v in status_counts.items()))
    if type_counts:
        logging.info("Event types → " + " | ".join(f"{k}: {v}" for k, v in type_counts.items()))
    if args.to_postgres:
        logging.info("Inserted valid events into Postgres.")
    if args.to_csv:
        logging.info("Wrote CSV to data/validated_orders.csv")
    logging.info(f"💵 min: {min_amt} | max: {max_amt}")
    if args.summary:
        summary = {
            "valid_events": ok,
            "errors": err,
            "total_amount": float(total),  # Decimal → float for JSON
            "avg_amount": float(avg),
            "status_counts": dict(status_counts),
            "event_type_counts": dict(type_counts),
        }
        out = Path("data/summary.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        logging.info(f"Wrote summary report to {out}")

    if args.summary_csv:
        out = Path("data/summary.csv")
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["valid_events", "errors", "total_amount", "avg_amount"])
            writer.writerow([ok, err, float(total), float(avg)])

            writer.writerow([])
            writer.writerow(["Status", "Count"])
            for k, v in status_counts.items():
                writer.writerow([k, v])

            writer.writerow([])
            writer.writerow(["Event Type", "Count"])
            for k, v in type_counts.items():
                writer.writerow([k, v])

        logging.info(f"Wrote summary report to {out}")

    if args.check_duplicates:
        logging.info(f"🔍 Found {duplicates} duplicate event_ids")
    if args.group_by and group_totals:
        formatted = " | ".join(f"{k}: {v:.2f}" for k, v in group_totals.items())
        logging.info(f"📊 Totals by {args.group_by} → {formatted}")


if __name__ == "__main__":
        main()
        



