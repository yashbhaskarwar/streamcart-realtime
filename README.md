# StreamCart Realtime ETL System

A project that simulates a real-time e-commerce data pipeline usig Python, Redpanda and Postgres.  

## Overview
The project showcases how online orders flow through a live data pipeline by covering everything from event generation to validation, logging and database storage.

## Architechture

                 +-------------------+
                 |    Producer       |
                 | (Python + Faker)  |
                 +---------+---------+
                           |
                           | order events (JSON)
                           v
                 +---------+---------+
                 |     Redpanda      |
                 |   (Kafka API)     |
                 +---------+---------+
                           |
                           | stream consume
                           v
                 +---------+---------+
                 |    Consumer       |
                 | (validate + stats |
                 |  + sink)          |
                 +----+-------+------+
                      |       |
        batch/file    |       | real-time sink
                      |       |
                      v       v
            +---------+--+  +----------------+
            | CSV / JSON |  |   Postgres     |
            | summaries  |  | orders_events  |
            +------------+  +----------------+

### Modes

- Batch mode: file → validate → stats → CSV/JSON/Postgres
- Streaming mode: Redpanda → validate → stats → Postgres

## Components
Producer <br>
Generates and logs fake e-commerce order events <br>
Publishes to Redpanda or writes to file <br>
Supports reproducible datasets and overwrite mode <br>

Consumer <br>
Validates events, calculates totals, averages, per-status and per-type counts <br>
Exports data to CSV or Postgres <br>
Supports multiple filters and reporting options <br>
Includes real-time streaming mode for consuming directly from Redpanda <br>
Throughput metrics and health checks <br>

## Features <br>

### Batch Mode
* JSON and CSV summaries
* Currency and amount filters
* Duplicate detection
* Min/Max stats
* Outlier detection
* Category enrichment
* Group by category
* Overwrite mode for clean datasets

### Streaming Mode
* Real-time Redpanda consumer
* --limit to stop after N events
* --print-events to print full JSON payloads
* --group-id to control Kafka consumer offset behavior
* --topic to consume from any topic 
* Real-time Postgres sink
* Throughput metrics with --metrics-every
* health checks before streaming 

## Run locally
```bash
# Dependencies
pip install -r requirements.txt
```

### Run Redpanda with Docker
```bash
# Start redpanda broker
docker compose -f docker-compose.redpanda.yml up -d

# Check status
docker ps
```

### Producer
```bash
# Generate events
python -m src.producer --count 5

# Reproducible events
python -m src.producer --count 5 --seed 42

# Overwrite previous dataset
python -m src.producer --count 50 --overwrite

# Publish directly to Redpanda
python -m src.producer --count 10 --to-redpanda
```

### Consumer
```bash
# Validate events 
python -m src.consumer --file data/orders_log.jsonl

# Validate and export to CSV
python -m src.consumer --file data/orders_log.jsonl --to-csv

# Filters
python -m src.consumer --file data/orders_log.jsonl --status DELIVERED,SHIPPED # by status
python -m src.consumer --file data/orders_log.jsonl --currency USD,INR # by currency
python -m src.consumer --file data/orders_log.jsonl --min-amount 50 --max-amount 300 # by amount range

# Duplicates & Outliers
python -m src.consumer --file data/orders_log.jsonl --check-duplicates
python -m src.consumer --file data/orders_log.jsonl --detect-outliers

# Group totals by category
python -m src.consumer --file data/orders_log.jsonl --group-by category

# Export summaries
python -m src.consumer --file data/orders_log.jsonl --summary
python -m src.consumer --file data/orders_log.jsonl --summary-csv

# Insert batch into Postgres
python -m src.consumer --file data/orders_log.jsonl --to-postgres
```

## Streaming Mode (Redpanda)
```bash
# Listen for live events
python -m src.consumer --from-redpanda --limit 5

# Print full event payloads
python -m src.consumer --from-redpanda --print-events --limit 3

# Use custom Kafka consumer group
python -m src.consumer --from-redpanda --group-id test1 --limit 5

# Choose custom topic
python -m src.consumer --from-redpanda --topic orders --limit 5

# Real-time Postgres sink + metrics
set PG_PORT=5433
python -m src.consumer --from-redpanda --to-postgres --metrics-every 20
```
### Postgres Integration
```bash
# Postgres client required
pip install psycopg2-binary

# Show table schema
python -m src.consumer --show-schema

# Validate and insert to Postgres
python -m src.consumer --file data/orders_log.jsonl --to-postgres
```

## Dashboard
Streamlit dashboard to show live order stats from Postgres.
```bash
set PG_PORT=5433  # for docker postgres
streamlit run src/dashboard.py
```
