import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # ← added

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
    )

conn = get_connection()

st.header("Crime Count VS Temperature",text_alignment="center")

# ── Selections now live in the sidebar ──────────────────────────
year = st.sidebar.selectbox("Select Year", ['-']+ list(range(2020, 2025)))
# limit = st.sidebar

@st.cache_data
def get_crime_by_day_in_each_year(year):
    query = f"""
        SELECT 
            date_occurred,
            COUNT(*) AS crime_count,
            AVG(average_temp) AS daily_avg_temperature_celsius  -- ← renamed to match plot
        FROM silver_crime_report_and_temperatures 
        {"" if year == '-' else "WHERE EXTRACT(YEAR FROM date_occurred) = %s"}
        GROUP BY date_occurred
        ORDER BY date_occurred
    """
    return pd.read_sql_query(query, conn, params=(year,))


daily_data = get_crime_by_day_in_each_year(year)  # ← renamed to match plot

# Plotting the relationship
plt.figure(figsize=(10, 6))

sns.regplot(
    data=daily_data,
    x='daily_avg_temperature_celsius',
    y='crime_count',
    scatter_kws={'alpha': 0.5, 's': 30, 'color': 'royalblue'},
    line_kws={'color': 'crimson', 'linewidth': 2},
    truncate=False
)

# Customize appearance
plt.xlim(daily_data['daily_avg_temperature_celsius'].min()-5, daily_data['daily_avg_temperature_celsius'].max()+5)
plt.title('Average Temperature vs Daily Crime Counts', fontsize=16)
plt.xlabel('Average Temperature (°F)', fontsize=12)
plt.ylabel('Daily Crime Counts', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)



plt.tight_layout()
st.pyplot(plt,True)