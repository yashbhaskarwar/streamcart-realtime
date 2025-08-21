# StreamCart Realtime — Day 1 (Professional Minimal)

A clean foundation for a streaming e‑commerce pipeline. Today’s version focuses on **data modeling** and **event simulation** without external systems yet.

## What’s included
- **OrderEvent schema** with Pydantic
- **Producer** that generates realistic fake orders (Faker) and prints JSON to stdout
- **Consumer stub** that validates events (no Kafka/DB yet)
- **Unit test** for schema
- **Professional structure** you can extend incrementally

## Run locally
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# Generate a few events
python src/producer.py --count 5

# Validate a sample event with the consumer stub
python src/consumer.py --sample
```

## Next steps (tomorrow / this week)
- Add Kafka/Redpanda and publish to `orders` topic
- Add a real consumer that reads from Kafka
- Create Postgres table schema & write inserts (UPSERT on event_id)
- Add GitHub Actions (ruff/black/pytest) and pre-commit hooks
- Add basic README architecture diagram
