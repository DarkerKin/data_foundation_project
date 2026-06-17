import psycopg2

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

# Postgres row count by year
cur.execute("""
    CREATE TABLE gold_crime_report_by_location AS
    SELECT *
    FROM silver_crime_reports 
    WHERE latitude != 0 or longitude != 0;
""")

conn.commit()
cur.close()
conn.close()