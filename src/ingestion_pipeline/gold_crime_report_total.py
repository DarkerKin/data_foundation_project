import psycopg2

# ── 1. Connect & Query ───────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE GOLD_CRIME_REPORT_BY_AREA AS
    SELECT division_name, COUNT(division_name) 
    AS crime_count
    FROM silver_crime_reports
    GROUP BY division_name
    ORDER BY COUNT(division_name) DESC
""")

conn.commit()

cur.close()
conn.close()