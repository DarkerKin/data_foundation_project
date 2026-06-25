import psycopg2
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── 1. Connect ───────────────────────────────────────────────────────
conn = psycopg2.connect(
    host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
)
cur = conn.cursor()

cur.execute("SELECT * FROM gold_crime_report_by_month")
db_rows = cur.fetchall()

cur.close()
conn.close()

month  = [row[0] for row in db_rows]
counts = [row[1] for row in db_rows]

# ── 3. Plot ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))

# Line + markers
ax.plot(month, counts, color="#4C72B0", linewidth=2, marker="o", markersize=6)

# Value labels on top of each point
for x, y in zip(month, counts):
    ax.text(
        x, y + max(counts) * 0.01,
        f"{y:,}",
        ha="center", va="bottom", fontsize=9, color="#333333"
    )

ax.set_title("Crime Reports by Month 2024", fontsize=15, fontweight="bold", pad=16)
ax.set_xlabel("Month", fontsize=11, labelpad=10)
ax.set_ylabel("Number of Reports", fontsize=11, labelpad=10)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_ylim(0, max(counts) * 1.12)

plt.xticks(rotation=45, ha="right", fontsize=9)
plt.tight_layout()
plt.savefig("crime_by_month.png", dpi=150)
plt.show()