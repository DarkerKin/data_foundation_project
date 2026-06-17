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
def get_crime_codes_by_year(year):
    query = """
        SELECT DISTINCT crime_code
        FROM gold_crime_report_by_location
        WHERE EXTRACT(YEAR FROM date_occurred) = %s
        ORDER BY crime_code;
    """
    return pd.read_sql_query(query, conn, params=(year,))

crime_codes_df = get_crime_codes_by_year(year)

if crime_codes_df.empty:
    st.sidebar.warning("No crime data found for this year.")
    st.stop()

crime_code = st.sidebar.selectbox("Select Crime Code", crime_codes_df["crime_code"])

@st.cache_data
def get_crime_locations(year, crime_code):
    query = """
        SELECT latitude, longitude
        FROM gold_crime_report_by_location
        WHERE EXTRACT(YEAR FROM date_occurred) = %s
          AND crime_code = %s;
    """
    return pd.read_sql_query(query, conn, params=(year, crime_code))

df = get_crime_locations(year, crime_code)
df = df.dropna(subset=["latitude", "longitude"])

if df.empty:
    st.warning("No location data available for this selection.")
else:
    st.map(df)