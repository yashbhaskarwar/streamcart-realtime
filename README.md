# StreamCart Realtime 

A project that simulates a real-time e-commerce data pipeline.  


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
