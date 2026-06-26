import streamlit as st
import psycopg2
import pandas as pd

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost", dbname="mydb", user="myuser", password="mypassword", port=5432
    )

conn = get_connection()

st.header("Crime Count by Crime Description",text_alignment="center")

# ── Selections now live in the sidebar ──────────────────────────
year = st.sidebar.selectbox("Select Year", ['-'] + list(range(2020, 2025)))
limit = st.sidebar.slider("Select Limit", 1, 100, 10)

@st.cache_data
def get_victim_descent_from_db(year):
    if year == '-':
        query = """
            SELECT DISTINCT victim_descent
            FROM silver_crime_reports
            ORDER BY victim_descent;
        """
        params = ()
    else:
        query = """
            SELECT DISTINCT victim_descent
            FROM silver_crime_reports
            WHERE EXTRACT(YEAR FROM date_occurred) = %s
            ORDER BY victim_descent;
        """
        params = (year,)
    return pd.read_sql_query(query, get_connection(), params=params)

victim_descent_df = get_victim_descent_from_db(year)

if victim_descent_df.empty:
    st.sidebar.warning("No crime data found for this year.")
    st.stop()

victim_descent = st.sidebar.selectbox(
    "Select victim descent",
    ['-'] + victim_descent_df["victim_descent"].tolist()
)

@st.cache_data
def get_crime_type_by_year(year, crime_limit, victim_descent):
    if year == '-' and victim_descent == '-':
        query = """
            SELECT crime_description, COUNT(*) as cases
            FROM silver_crime_reports
            GROUP BY crime_description
            ORDER BY cases DESC
            LIMIT %s;
        """
        params = (crime_limit,)
    elif year == '-':
        query = """
            SELECT crime_description, COUNT(*) as cases
            FROM silver_crime_reports
            WHERE victim_descent = %s
            GROUP BY crime_description
            ORDER BY cases DESC
            LIMIT %s;
        """
        params = (victim_descent, crime_limit)
    elif victim_descent == '-':
        query = """
            SELECT crime_description, COUNT(*) as cases
            FROM silver_crime_reports
            WHERE EXTRACT(YEAR FROM date_occurred) = %s
            GROUP BY crime_description
            ORDER BY cases DESC
            LIMIT %s;
        """
        params = (year, crime_limit)
    else:
        query = """
            SELECT crime_description, COUNT(*) as cases
            FROM silver_crime_reports
            WHERE EXTRACT(YEAR FROM date_occurred) = %s
              AND victim_descent = %s
            GROUP BY crime_description
            ORDER BY cases DESC
            LIMIT %s;
        """
        params = (year, victim_descent, crime_limit)

    return pd.read_sql_query(query, get_connection(), params=params)

crime_by_type_df = get_crime_type_by_year(year, limit, victim_descent)

# Sort the DataFrame before passing to bar_chart (sort parameter doesn't exist in st.bar_chart)
crime_by_type_df = crime_by_type_df.sort_values("cases", ascending=False)

st.bar_chart(crime_by_type_df, x="crime_description", y="cases",sort="-cases")