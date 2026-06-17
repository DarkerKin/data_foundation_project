import psycopg2
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── 1. Connect & Query ───────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

cur.execute("""
    SELECT * FROM GOLD_CRIME_REPORT_BY_AREA
""")
db_rows = cur.fetchall()

cur.close()
conn.close()

# ── 2. Unpack results ────────────────────────────────────────────────
divisions = [row[0] for row in db_rows]
counts    = [row[1] for row in db_rows]

# ── 3. Plot ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))

bars = ax.bar(divisions, counts, color="#4C72B0", edgecolor="white", linewidth=0.6)

# Value labels on top of each bar
for bar, count in zip(bars, counts):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(counts) * 0.01,
        f"{count:,}",
        ha="center", va="bottom", fontsize=9, color="#333333"
    )

ax.set_title("Crime Reports by Division", fontsize=15, fontweight="bold", pad=16)
ax.set_xlabel("Division", fontsize=11, labelpad=10)
ax.set_ylabel("Number of Reports", fontsize=11, labelpad=10)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_ylim(0, max(counts) * 1.12)

plt.xticks(rotation=45, ha="right", fontsize=9)
plt.tight_layout()
plt.savefig("crime_by_division.png", dpi=150)
plt.show()