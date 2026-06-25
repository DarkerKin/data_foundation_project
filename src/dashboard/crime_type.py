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
limit = st.sidebar.slider("Select Limit", 1, 100, 10)

@st.cache_data
def get_crime_type_by_year(year, crime_limit):
    if year == '-':
        query = """
            SELECT crime_description, COUNT(*) as cases
            FROM silver_crime_reports
            GROUP BY crime_description
            ORDER BY cases DESC
            LIMIT %s;
        """
        params = (crime_limit,)
    else:
        query = """
            SELECT crime_description, COUNT(*) as cases
            FROM silver_crime_reports
            WHERE EXTRACT(YEAR FROM date_occurred) = %s
            GROUP BY crime_description
            ORDER BY cases DESC
            LIMIT %s;
        """
        params = (year, crime_limit)

    return pd.read_sql_query(query, conn, params=params)

crime_by_type_df = get_crime_type_by_year(year, limit)

st.bar_chart(crime_by_type_df,x="crime_description",y="cases",sort="-cases")