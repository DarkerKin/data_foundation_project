import psycopg2

conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()
cur.execute("""
        CREATE TABLE silver_temperature AS
        SELECT *
        FROM bronze_temperature
    """)

cur.execute("""
    ALTER TABLE silver_temperature
    ADD COLUMN IF NOT EXISTS average_temperature NUMERIC;
""")

cur.execute("""
    UPDATE silver_temperature
    SET average_temperature = round((temp_min + temp_max) / 2.0,2);
""")

#do not need these columns
cur.execute("""
    ALTER TABLE silver_temperature DROP COLUMN temp_min, DROP COLUMN temp_max;
""")

conn.commit()
cur.close()
conn.close()