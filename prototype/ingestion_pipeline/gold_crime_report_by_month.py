import psycopg2

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

# Postgres row count by year
cur.execute("""
    CREATE TABLE gold_crime_report_by_month AS
    SELECT TO_CHAR(date_occurred, 'Month') AS month_name, COUNT(*) 
    FROM silver_crime_reports 
    WHERE EXTRACT(YEAR FROM date_occurred) = 2024
    GROUP BY TO_CHAR(date_occurred, 'Month'), EXTRACT(MONTH FROM date_occurred)
    ORDER BY EXTRACT(MONTH FROM date_occurred)
""")

conn.commit()
cur.close()
conn.close()