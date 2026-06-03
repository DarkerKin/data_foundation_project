import psycopg2

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

# Postgres row count
cur.execute("SELECT COUNT(*) FROM bronze_crime_reports")
db_rows = cur.fetchone()[0]

print(f"DB rows:    {db_rows}")

cur.close()