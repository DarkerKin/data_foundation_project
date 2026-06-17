import psycopg2

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

#create a new silver table
cur.execute("""
    CREATE TABLE silver_crime_report_and_temperatures AS
    SELECT report_id, date_occurred, time_occurred, division_code, division_name, reporting_district, crime_code,crime_description, victim_age, victim_sex, victim_descent, weapon_code, weapon_description,address, latitude, longitude 
    FROM bronze_crime_reports
""")

#join and add the avg temp and precipitation from silver temp to the silver crime table
cur.execute("""
    ALTER TABLE silver_crime_report_and_temperatures
    ADD COLUMN average_temp NUMERIC,
    ADD COLUMN precipitation_mm NUMERIC;
""")

cur.execute("""
    UPDATE silver_crime_report_and_temperatures r
    SET 
        average_temp = t.average_temperature,
        precipitation_mm = t.precipitation_mm
    FROM silver_temperature t
    WHERE r.date_occurred = t.time;
""")


conn.commit()
cur.close()
conn.close()

