from __future__ import annotations
import json, random, argparse, uuid
from datetime import datetime, timezone
from faker import Faker
from src.common.models import OrderEvent
from decimal import Decimal

fake = Faker()

def make_order_event() -> dict:
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    customer_id = f"cus_{fake.random_number(digits=4)}"
    status = random.choice(["PLACED","CONFIRMED","SHIPPED","DELIVERED"])
    evt_type = random.choice(["order_created","order_updated"])
    amount = Decimal(str(round(random.uniform(5, 500), 2)))
    currency = random.choice(["USD","EUR","GBP","INR"]) or "USD"
    items = random.randint(1, 5)
    evt = OrderEvent(
        event_type=evt_type,
        event_ts=datetime.now(timezone.utc),
        order_id=order_id,
        customer_id=customer_id,
        status=status,
        amount=amount,
        currency=currency,
        items_count=items,
    )
    return json.loads(evt.model_dump_json())

def main():
    parser = argparse.ArgumentParser(description="Generate fake order events")
    parser.add_argument("--count", type=int, default=3, help="number of events to generate")
    parser.add_argument("--seed", type=int, help="random seed for reproducible events") # For reproducible output
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        Faker.seed(args.seed)
        
    # ensure data folder exists
    import os
    os.makedirs("data", exist_ok=True)

    log_file = "data/orders_log.jsonl"

    for _ in range(args.count):
        evt = make_order_event()
        line = json.dumps(evt, default=str)

        # print to stdout
        print(line)

        # append to log file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    print(f"Wrote {args.count} events to {log_file}")


if __name__ == "__main__":
    main()
