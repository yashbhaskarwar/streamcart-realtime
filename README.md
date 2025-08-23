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
python src/producer.py --count 5

# Validate a sample event with the consumer stub
python src/consumer.py --sample
```

