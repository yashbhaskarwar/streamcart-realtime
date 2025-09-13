# StreamCart Realtime (In Progress)

A project that simulates a real-time e-commerce data pipeline.  

Status
Producer generates and logs fake e-commerce order events  
Consumer validates events, prints totals, averages, status and event type counts  
Postgres integration for storing validated events  (optional for now)


## Run locally
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# Producer

# Generate a few events
python -m src.producer --count 5

# Generate reproducible events
python -m src.producer --count 5 --seed 42

# Consumer

# Validate events from the log file
python -m src.consumer --file data/orders_log.jsonl

# Show database schema (Postgres)
python -m src.consumer --show-schema

# Validate and insert into Postgres
python -m src.consumer --file data/orders_log.jsonl --to-postgres

# Validate and export to CSV
python -m src.consumer --file data/orders_log.jsonl --to-csv

# Filter by one or more statuses
python -m src.consumer --file data/orders_log.jsonl --status DELIVERED,SHIPPED

## Run tests
pytest -q

# Postgres client required
pip install psycopg2-binary

# Validate and insert to Postgres
python -m src.consumer --file data/orders_log.jsonl --to-postgres
```

## Sample Output

### Producer

```bash
python -m src.producer --count 3 --seed 42
```

### Example
{"event_id": "2be79b90-fc27-40e0-a3db-e82f7df39e38", "event_type": "order_created", "event_ts": "2025-09-13T23:13:04.488493Z", "order_id": "ord_cb06a1de", "customer_id": "cus_1824", "status": "PLACED", "amount": "372.07", "currency": "EUR", "items_count": 2} <br>
{"event_id": "bdd4f335-9a12-4ae9-bc9e-81e3de383cd5", "event_type": "order_created", "event_ts": "2025-09-13T23:13:04.494315Z", "order_id": "ord_2400e715", "customer_id": "cus_409", "status": "CONFIRMED", "amount": "339.97", "currency": "USD", "items_count": 5} <br>
{"event_id": "191071e2-041e-44d0-8c29-65f3b47482b4", "event_type": "order_created", "event_ts": "2025-09-13T23:13:04.496274Z", "order_id": "ord_bcfc9dc1", "customer_id": "cus_4506", "status": "DELIVERED", "amount": "19.75", "currency": "EUR", "items_count": 2} <br>

### Consumer
```bash
python -m src.consumer --file data/orders_log.jsonl
```

### Example
[INFO] ✅ 51 events valid | ❌ 0 errors | 💵 total: 13347.87 | avg: 261.72 <br>
[INFO] Status counts → PLACED: 14 | DELIVERED: 14 | SHIPPED: 12 | CONFIRMED: 11 <br>
[INFO] Event types → order_created: 29 | order_updated: 22


