import requests
import psycopg2
import re
import threading
import queue
import time
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────
API_WORKERS       = 5
BATCH_SIZE        = 50
CALLS_PER_SECOND  = 8
SENTINEL          = None

# ── Rate Limiter ──────────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, calls_per_second):
        self.calls_per_second = calls_per_second
        self.lock             = threading.Lock()
        self.last_call        = 0

    def wait(self):
        with self.lock:
            now       = time.time()
            gap       = 1.0 / self.calls_per_second
            wait_time = gap - (now - self.last_call)
            if wait_time > 0:
                time.sleep(wait_time)
            self.last_call = time.time()

rate_limiter = RateLimiter(calls_per_second=CALLS_PER_SECOND)

# ── Queues ────────────────────────────────────────────────────────────
date_queue   = queue.Queue()
result_queue = queue.Queue()

# ── Counters ──────────────────────────────────────────────────────────
stats = {
    "fetched"  : 0,
    "inserted" : 0,
    "skipped"  : 0,
    "failed"   : 0,
}
stats_lock = threading.Lock()

def increment(key, n=1):
    with stats_lock:
        stats[key] += n

# ── 1. Connect & setup ────────────────────────────────────────────────
print("Connecting to database...")
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

# Create temperature table
cur.execute("""
    CREATE TABLE IF NOT EXISTS temperature (
        id          SERIAL      PRIMARY KEY,
        time        DATE        UNIQUE,
        temp_max    NUMERIC(5,2),
        temp_min    NUMERIC(5,2)
    )
""")
conn.commit()

# Fetch already-processed dates so we don't re-fetch them
cur.execute("SELECT time FROM temperature")
already_done = {row[0].strftime("%Y-%m-%d") for row in cur.fetchall()}
print(f"Already in temperature table : {len(already_done):,} dates")

# Fetch distinct dates from source table
cur.execute("SELECT COUNT(DISTINCT date_occurred) FROM bronze_crime_reports")
total_distinct = cur.fetchone()[0]
print(f"Distinct dates in source     : {total_distinct:,}")

cur.execute("SELECT DISTINCT date_occurred FROM bronze_crime_reports")
db_rows = cur.fetchall()
cur.close()
conn.close()

# ── 2. Producer ───────────────────────────────────────────────────────
def producer():
    while True:
        item = date_queue.get()
        if item is SENTINEL:
            date_queue.task_done()
            break

        date_occurred = item
        match = re.search(r'\d{2}/\d{2}/\d{4}', str(date_occurred))
        if not match:
            print(f"  [producer] Could not parse date: {date_occurred}")
            increment("failed")
            date_queue.task_done()
            continue

        formatted_date = datetime.strptime(match.group(), "%m/%d/%Y").strftime("%Y-%m-%d")

        # Skip if already in DB
        if formatted_date in already_done:
            increment("skipped")
            date_queue.task_done()
            continue

        parsed_date = datetime.strptime(formatted_date, "%Y-%m-%d")
        today       = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        base_url    = "https://api.open-meteo.com/v1/forecast" if parsed_date >= today \
                      else "https://archive-api.open-meteo.com/v1/archive"

        url = (
            f"{base_url}"
            f"?latitude=34.0522&longitude=-118.2437"
            f"&daily=temperature_2m_max,temperature_2m_min"
            f"&temperature_unit=fahrenheit"
            f"&start_date={formatted_date}&end_date={formatted_date}"
            f"&timezone=America%2FLos_Angeles"
        )

        try:
            rate_limiter.wait()
            response = requests.get(url, timeout=10)

            # Backoff on rate limit
            if response.status_code == 429:
                print(f"  [producer] Rate limited — backing off 60s...")
                time.sleep(60)
                response = requests.get(url, timeout=10)

            response.raise_for_status()
            data     = response.json()
            time_val = data["daily"]["time"][0]
            temp_max = data["daily"]["temperature_2m_max"][0]
            temp_min = data["daily"]["temperature_2m_min"][0]

            result_queue.put((time_val, temp_max, temp_min))
            increment("fetched")
            print(f"  [producer] {time_val}  max={temp_max}°F  min={temp_min}°F")

        except requests.exceptions.Timeout:
            print(f"  [producer] Timeout        : {formatted_date}")
            increment("failed")
        except requests.exceptions.HTTPError as e:
            print(f"  [producer] HTTP error     : {formatted_date} — {e}")
            increment("failed")
        except requests.exceptions.RequestException as e:
            print(f"  [producer] Request failed : {formatted_date} — {e}")
            increment("failed")
        except (KeyError, IndexError) as e:
            print(f"  [producer] Bad response   : {formatted_date} — {e}")
            increment("failed")
        finally:
            date_queue.task_done()

# ── 3. Consumer ───────────────────────────────────────────────────────
def consumer():
    db_conn = psycopg2.connect(
        host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
    )
    db_cur = db_conn.cursor()
    batch  = []

    def flush():
        if not batch:
            return
        db_cur.executemany("""
            INSERT INTO temperature (time, temp_max, temp_min)
            VALUES (%s, %s, %s)
            ON CONFLICT (time) DO NOTHING
        """, batch)
        db_conn.commit()
        increment("inserted", len(batch))
        print(f"  [consumer] inserted batch of {len(batch)}")
        batch.clear()

    while True:
        item = result_queue.get()
        if item is SENTINEL:
            flush()
            result_queue.task_done()
            break

        batch.append(item)
        result_queue.task_done()

        if len(batch) >= BATCH_SIZE:
            flush()

    db_cur.close()
    db_conn.close()

# ── 4. Run ────────────────────────────────────────────────────────────
start_time = time.time()
print(f"\nStarting pipeline with {API_WORKERS} workers...\n")

# Fill date queue
for (date_occurred,) in db_rows:
    date_queue.put(date_occurred)
for _ in range(API_WORKERS):
    date_queue.put(SENTINEL)

# Start threads
producers = [threading.Thread(target=producer) for _ in range(API_WORKERS)]
consumer_thread = threading.Thread(target=consumer)

for p in producers:
    p.start()
consumer_thread.start()

for p in producers:
    p.join()
result_queue.put(SENTINEL)
consumer_thread.join()

# ── 5. Summary ────────────────────────────────────────────────────────
elapsed = time.time() - start_time
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Done in {elapsed:.1f}s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total distinct dates : {total_distinct:>8,}
  Already in DB        : {len(already_done):>8,}
  Fetched from API     : {stats['fetched']:>8,}
  Inserted into DB     : {stats['inserted']:>8,}
  Skipped (duplicate)  : {stats['skipped']:>8,}
  Failed               : {stats['failed']:>8,}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")