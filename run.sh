#!/bin/bash
set -e

docker compose -f config/docker-compose.yml up -d

# Wait for Docker services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Download data only if it doesn't exist
if [ ! -f data/crime_data.csv ]; then
    mkdir -p data
    curl -o ./data/crime_data.csv "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"
fi

# Create virtual env only if it doesn't exist
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

python3 src/ingestion_pipeline/bronze_crime_report.py
python3 src/ingestion_pipeline/bronze_temperature.py

python3 src/ingestion_pipeline/silver_crime_report.py
python3 src/ingestion_pipeline/silver_temperature.py
python3 src/ingestion_pipeline/silver_crime_report_temperature.py

python3 src/ingestion_pipeline/gold_crime_report_total.py
python3 src/ingestion_pipeline/gold_crime_report_by_type.py
python3 src/ingestion_pipeline/gold_crime_report_by_month.py
python3 src/ingestion_pipeline/gold_crime_report_by_location.py

streamlit run src/dashboard/app.py