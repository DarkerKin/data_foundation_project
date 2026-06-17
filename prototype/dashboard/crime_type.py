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
year = st.sidebar.selectbox("Select Year", ['-']+ list(range(2020, 2025)))

@st.cache_data
def get_crime_type_by_year(year):
    query = f"""
        SELECT crime_description, COUNT(*)  as cases
        FROM silver_crime_reports
        {"" if year == '-' else "WHERE EXTRACT(YEAR FROM date_occurred) = %s"}
        GROUP BY crime_description
        ORDER BY cases desc;
    """
    return pd.read_sql_query(query, conn, params=(year,))

crime_by_type_df = get_crime_type_by_year(year)

st.bar_chart(crime_by_type_df,x="crime_description",y="cases",sort="-cases")