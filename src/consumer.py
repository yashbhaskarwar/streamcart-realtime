from __future__ import annotations
import argparse, json, sys
from src.common.models import OrderEvent

def validate_event(payload: dict) -> OrderEvent:
    return OrderEvent(**payload)

def main():
    parser = argparse.ArgumentParser(description="Consumer stub that validates one sample event")
    parser.add_argument("--sample", action="store_true", help="validate a hard-coded sample event")
    args = parser.parse_args()

    if args.sample:
        sample = {
            "event_type": "order_created",
            "event_ts": "2025-08-20T00:00:00+00:00",
            "order_id": "ord_123456",
            "customer_id": "cus_1234",
            "status": "PLACED",
            "amount": 19.99,
            "currency": "USD",
            "items_count": 2,
        }
        evt = validate_event(sample)
        print("validated:", evt.model_dump())
    else:
        try:
            payload = json.loads(sys.stdin.read())
            evt = validate_event(payload)
            print("validated:", evt.model_dump())
        except Exception as e:
            print("error:", str(e))
            sys.exit(1)

if __name__ == "__main__":
    main()
