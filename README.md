# StreamCart Realtime — Day 1 (Professional Minimal)

A clean foundation for a streaming e‑commerce pipeline. Today’s version focuses on **data modeling** and **event simulation** without external systems yet.

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

