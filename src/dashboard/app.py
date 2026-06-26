import streamlit as st


pg = st.navigation([
    st.Page("crime_location.py", title="Crime Occurred in which location", icon="👮🏽‍♀️"),
    st.Page("crime_by_month.py", title="Crime count per month", icon="👮🏻‍♂️"),
    st.Page("crime_type.py", title="Crime count per type", icon="👮🏻‍♂️"),
    st.Page("crime_temperature.py", title="correlation between temperature and crime count", icon="👮🏻‍♂️"),
])
pg.run()