import streamlit as st


pg = st.navigation([
    st.Page("crime_location.py", title="Crime Occurred", icon="👮🏽‍♀️"),
    st.Page("crime_by_month.py", title="Second page", icon=":material/favorite:"),
    st.Page("crime_type.py", title="third page", icon="👩🏻‍🍳"),
])
pg.run()