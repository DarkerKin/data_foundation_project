import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

# Postgres row count
cur.execute("SELECT * FROM gold_crime_report_by_type order by cases asc limit 10;")
db_rows = cur.fetchall()

cur.close()
conn.close()

df = pd.DataFrame(db_rows,columns=['type_of_crime','crime_rate'])

plt.barh(df['type_of_crime'],df['crime_rate'])
plt.show()