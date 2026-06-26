import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session

st.set_page_config(layout="wide", page_title="Hotel Analytics")

st.markdown("""
<style>
    .stApp { background-color: #0c121e; color: white; }
    [data-testid="stMetricValue"] {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 20px;
        border: 2px solid #3b82f6;
        text-align: center;
        color: #60a5fa !important;
    }
</style>
""", unsafe_allow_html=True)

session = get_active_session()

@st.cache_data(ttl=600)
def load_data():
    return session.sql("SELECT * FROM HOTEL_DB.PUBLIC.GOLD_BOOKING_CLEAN").to_pandas()

df = load_data()

st.title("Hotel Performance Dashboard")
st.markdown("---")

# 1. (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${df['TOTAL_AMOUNT'].sum():,.0f}")
col2.metric("Total Bookings", len(df))
col3.metric("Avg Booking", f"${df['TOTAL_AMOUNT'].mean():,.0f}")
col4.metric("Unique Cities", df['HOTEL_CITY'].nunique())

st.markdown("---")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Revenue Trend (Area Gradient)")
    df['CHECK_IN_DATE'] = pd.to_datetime(df['CHECK_IN_DATE'])
    daily_df = df.groupby('CHECK_IN_DATE')['TOTAL_AMOUNT'].sum().reset_index()
    
    #  (Gradient)
    chart = alt.Chart(daily_df).mark_area(
        line={'color': '#1fcd7b'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='#1fcd7b', offset=0),
                   alt.GradientStop(color='transparent', offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x='CHECK_IN_DATE:T',
        y='TOTAL_AMOUNT'
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

with c2:
    st.subheader("Top Cities by Revenue")
    city_df = df.groupby('HOTEL_CITY')['TOTAL_AMOUNT'].sum().nlargest(10).reset_index()
    
    
    chart_bar = alt.Chart(city_df).mark_bar(color='#3b5998').encode(
        x='TOTAL_AMOUNT', 
        y=alt.Y('HOTEL_CITY', sort='-x')
    ).properties(height=300)
    st.altair_chart(chart_bar, use_container_width=True)


st.subheader("Detailed Records")
st.dataframe(df, use_container_width=True)

with st.sidebar:
    st.header("Filters")
    selected_cities = st.multiselect("Select Cities:", options=df['HOTEL_CITY'].unique().tolist())
    st.info("Dashboard auto-updates.")