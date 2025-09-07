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

# Generate a few events
python -m src.producer --count 5

# Validate events from the log file
python -m src.consumer --file data/orders_log.jsonl

## Run tests
pytest -q

# Postgres client required
pip install psycopg2-binary

# Validate and insert to Postgres
python -m src.consumer --file data/orders_log.jsonl --to-postgres

