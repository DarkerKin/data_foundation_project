import psycopg2

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

#create a new silver table
cur.execute("""
    CREATE TABLE silver_crime_reports AS
    SELECT report_id, date_occurred, time_occurred, division_code, division_name, reporting_district, crime_code,crime_description, victim_age, victim_sex, victim_descent, weapon_code, weapon_description,address, latitude, longitude 
    FROM bronze_crime_reports
""")

#first convert the date occurred from string to date
cur.execute("""
    ALTER TABLE silver_crime_reports
    ALTER COLUMN date_occurred TYPE DATE
    USING TO_DATE(TRIM(date_occurred), 'MM/DD/YYYY');
""")

#join renamed the descent to more definitive 
cur.execute("""
    UPDATE silver_crime_reports
    SET victim_descent = CASE victim_descent
        WHEN 'W' THEN 'White'
        WHEN 'B' THEN 'Black'
        WHEN 'H' THEN 'Hispanic'
        WHEN 'A' THEN 'Asian'
        WHEN 'O' THEN 'Other'
        WHEN 'I' THEN 'American Indian/Alaskan Native'
        WHEN 'P' THEN 'Pacific Islander'
        WHEN 'F' THEN 'Filipino'
        WHEN 'C' THEN 'Chinese'
        WHEN 'J' THEN 'Japanese'
        WHEN 'K' THEN 'Korean'
        WHEN 'V' THEN 'Vietnamese'
        WHEN 'Z' THEN 'Cambodian'
        ELSE 'Unknown'
    END;
""")

# change the victim sex to more appropriate thing
cur.execute("""
    UPDATE silver_crime_reports
    SET victim_sex = CASE victim_sex
        WHEN 'M' THEN 'male'
        WHEN 'F' THEN 'female'
        WHEN 'H' THEN 'other'
        ELSE 'Unknown'
    END;
""")



conn.commit()
cur.close()
conn.close()

