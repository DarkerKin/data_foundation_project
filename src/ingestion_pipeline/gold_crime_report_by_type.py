import psycopg2

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

# Postgres row count by year
cur.execute("""
    CREATE TABLE gold_crime_report_by_type AS
    SELECT crime_description, COUNT(*)  as cases
    FROM silver_crime_reports
    GROUP BY crime_description
    ORDER BY cases desc;
""")

conn.commit()
cur.close()
conn.close()