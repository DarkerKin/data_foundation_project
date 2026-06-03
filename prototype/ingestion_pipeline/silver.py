import psycopg2

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

# Postgres row count
cur.execute("SELECT * FROM bronze_crime_reports WHERE crime_code <> crime_code_1;")
db_rows = cur.fetchall()


for db_row in db_rows:
    print(db_row)

cur.close()
conn.close()

