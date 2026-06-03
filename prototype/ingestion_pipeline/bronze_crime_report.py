import psycopg2
import csv

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

# ── 2. Create table ──────────────────────────────────────────────────
cur.execute("""
    CREATE TABLE IF NOT EXISTS bronze_crime_reports (
        report_id             BIGINT PRIMARY KEY,
        date_reported         TEXT,
        date_occurred         TEXT,
        time_occurred         BIGINT,
        division_code         BIGINT,
        division_name         TEXT,
        reporting_district    BIGINT,
        crime_severity        BIGINT,
        crime_code            BIGINT,
        crime_description     TEXT,
        modus_operandi        TEXT,
        victim_age            BIGINT,
        victim_sex            TEXT,
        victim_descent        TEXT,
        premise_code          FLOAT,
        premise_description   TEXT,
        weapon_code           FLOAT,
        weapon_description    TEXT,
        status_code           TEXT,
        status_description    TEXT,
        crime_code_1          FLOAT,
        crime_code_2          FLOAT,
        crime_code_3          FLOAT,
        crime_code_4          FLOAT,
        address               TEXT,
        cross_street          TEXT,
        latitude              FLOAT,
        longitude             FLOAT
    )
""")
conn.commit()

# ── 3. Column mapping (CSV header -> DB column) ──────────────────────
column_map = {
    'DR_NO'         : 'report_id',
    'Date Rptd'     : 'date_reported',
    'DATE OCC'      : 'date_occurred',
    'TIME OCC'      : 'time_occurred',
    'AREA'          : 'division_code',
    'AREA NAME'     : 'division_name',
    'Rpt Dist No'   : 'reporting_district',
    'Part 1-2'      : 'crime_severity',
    'Crm Cd'        : 'crime_code',
    'Crm Cd Desc'   : 'crime_description',
    'Mocodes'       : 'modus_operandi',
    'Vict Age'      : 'victim_age',
    'Vict Sex'      : 'victim_sex',
    'Vict Descent'  : 'victim_descent',
    'Premis Cd'     : 'premise_code',
    'Premis Desc'   : 'premise_description',
    'Weapon Used Cd': 'weapon_code',
    'Weapon Desc'   : 'weapon_description',
    'Status'        : 'status_code',
    'Status Desc'   : 'status_description',
    'Crm Cd 1'      : 'crime_code_1',
    'Crm Cd 2'      : 'crime_code_2',
    'Crm Cd 3'      : 'crime_code_3',
    'Crm Cd 4'      : 'crime_code_4',
    'LOCATION'      : 'address',
    'Cross Street'  : 'cross_street',
    'LAT'           : 'latitude',
    'LON'           : 'longitude',
}

# ── 4. Insert rows ───────────────────────────────────────────────────
db_columns = list(column_map.values())
csv_columns = list(column_map.keys())

insert_query = f"""
    INSERT INTO bronze_crime_reports ({', '.join(db_columns)})
    VALUES ({', '.join(['%s'] * len(db_columns))})
"""

with open("./data/crime_data.csv", "r") as f:
    reader = csv.DictReader(f)
    batch = []

    for row in reader:
        values = tuple(row[col] if row[col] != '' else None for col in csv_columns)
        batch.append(values)

        # Insert in batches of 1000 for performance
        if len(batch) == 1000:
            cur.executemany(insert_query, batch)
            conn.commit()
            batch = []

    # Insert remaining rows
    if batch:
        cur.executemany(insert_query, batch)
        conn.commit()

print("Done!")
cur.close()
conn.close()