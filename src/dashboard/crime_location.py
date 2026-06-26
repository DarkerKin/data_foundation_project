import streamlit as st
import psycopg2
import pandas as pd

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
    )

conn = get_connection()

st.header("Crime Location in LA", text_alignment="center")

# ── Selections now live in the sidebar ──────────────────────────
year = st.sidebar.selectbox("Select Year", list(range(2020, 2025)))

@st.cache_data
def get_crime_descriptions_by_year(year):
    query = """
        SELECT DISTINCT crime_description
        FROM gold_crime_report_by_location
        WHERE EXTRACT(YEAR FROM date_occurred) = %s
        ORDER BY crime_description;
    """
    return pd.read_sql_query(query, conn, params=(year,))

crime_descriptions_df = get_crime_descriptions_by_year(year)

if crime_descriptions_df.empty:
    st.sidebar.warning("No crime data found for this year.")
    st.stop()

crime_description = st.sidebar.selectbox("Select Crime Description", crime_descriptions_df["crime_description"])

@st.cache_data
def get_crime_locations(year, crime_description):
    query = """
        SELECT latitude, longitude
        FROM gold_crime_report_by_location
        WHERE EXTRACT(YEAR FROM date_occurred) = %s
          AND crime_description = %s;
    """
    return pd.read_sql_query(query, conn, params=(year, crime_description))

df = get_crime_locations(year, crime_description)
df = df.dropna(subset=["latitude", "longitude"])

if df.empty:
    st.warning("No location data available for this selection.")
else:
    st.map(df)