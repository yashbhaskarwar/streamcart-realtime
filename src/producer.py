from __future__ import annotations
import json, random, argparse, uuid
from datetime import datetime, timezone
from faker import Faker
from src.common.models import OrderEvent
from decimal import Decimal
from confluent_kafka import Producer as KafkaProducer

fake = Faker()
CATEGORIES = ["electronics", "fashion", "groceries", "beauty", "sports", "books"]

def make_order_event(forced_currency: str | None = None) -> dict:
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    customer_id = f"cus_{fake.random_number(digits=4)}"
    status = random.choice(["PLACED","CONFIRMED","SHIPPED","DELIVERED"])
    evt_type = random.choice(["order_created","order_updated"])
    amount = Decimal(str(round(random.uniform(5, 500), 2)))
    currency = forced_currency or random.choice(["USD", "EUR", "GBP", "INR"])
    items = random.randint(1, 5)
    category = random.choice(CATEGORIES)
    evt = OrderEvent(
        event_type=evt_type,
        event_ts=datetime.now(timezone.utc),
        order_id=order_id,
        customer_id=customer_id,
        status=status,
        amount=amount,
        currency=currency,
        items_count=items,
        category=category,
    )
    return json.loads(evt.model_dump_json())

def main():
    parser = argparse.ArgumentParser(description="Generate fake order events")
    parser.add_argument("--count", type=int, default=3, help="number of events to generate")
    parser.add_argument("--seed", type=int, help="random seed for reproducible events") # For reproducible output
    parser.add_argument(
    "--currency",
    type=str,
    help="Force all orders to use this currency (e.g., USD, EUR, INR)",
    )
    parser.add_argument(
    "--overwrite",
    action="store_true",
    help="If set, replace existing data/orders_log.jsonl instead of appending"
    )
    parser.add_argument(
    "--to-redpanda",
    action="store_true",
    help="If set, publish events to a Redpanda topic (in addition to writing to file)"
    )

    args = parser.parse_args()

    forced_currency = args.currency.upper() if args.currency else None

    if args.seed is not None:
        random.seed(args.seed)
        Faker.seed(args.seed)
        
    # ensure data folder exists
    import os
    os.makedirs("data", exist_ok=True)

    log_file = "data/orders_log.jsonl"

    # overwrite or append
    mode = "w" if args.overwrite else "a"
    if args.overwrite:
        print(f"[INFO] Overwriting existing log file: {log_file}")

    kafka_producer = None
    if args.to_redpanda:
        kafka_producer = KafkaProducer({"bootstrap.servers": "localhost:9092"})
        topic = "orders"

    for _ in range(args.count):
        evt = make_order_event(forced_currency=forced_currency)
        line = json.dumps(evt, default=str)
        print(line)
        with open(log_file, mode, encoding="utf-8") as f:
            f.write(line + "\n")
        mode = "a"
    
        # publish to Redpanda
        if kafka_producer:
            kafka_producer.produce(topic, value=line.encode("utf-8"))
            # kafka_producer.flush(0.1)
    if kafka_producer:
        kafka_producer.flush() 

    print(f"Wrote {args.count} events to {log_file}")


if __name__ == "__main__":
    main()