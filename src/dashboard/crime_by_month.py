import streamlit as st
import psycopg2
import pandas as pd

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
    )

conn = get_connection()

# ── Selections now live in the sidebar ──────────────────────────
year = st.sidebar.selectbox("Select Year", list(range(2020, 2025)))

@st.cache_data
def get_crime_by_month_in_each_year(year):
    query = """
        SELECT TO_CHAR(date_occurred, 'Month') AS month_name, COUNT(*) AS crime_rate
        FROM silver_crime_reports 
        WHERE EXTRACT(YEAR FROM date_occurred) = %s
        GROUP BY TO_CHAR(date_occurred, 'Month'), EXTRACT(MONTH FROM date_occurred)
        ORDER BY EXTRACT(MONTH FROM date_occurred)
    """
    return pd.read_sql_query(query, conn, params=(year,))

crime_by_month_df = get_crime_by_month_in_each_year(year)

st.bar_chart(crime_by_month_df,x="month_name",y="crime_rate",sort=False)
