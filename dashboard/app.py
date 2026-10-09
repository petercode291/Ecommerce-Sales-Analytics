import streamlit as st
import pandas as pd
import sqlite3
import subprocess
import pickle
from pathlib import Path
import datetime

st.set_page_config(layout="wide")

# Bootstrapper for Streamlit Cloud
db_path = Path("data/processed/ecommerce.db")
if not db_path.exists():
    with st.spinner('Initializing database and training model...'):
        subprocess.run(["python", "src/clean.py"])
        subprocess.run(["python", "src/train_model.py"])


@st.cache_data
def load_data():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(
        "SELECT DATE(order_timestamp) as dt, order_id, country, category, net_revenue FROM delivered_revenue", conn)
    df['dt'] = pd.to_datetime(df['dt'])
    conn.close()
    return df


df = load_data()

st.sidebar.header("Filters")
selected_cat = st.sidebar.multiselect("Category", df['category'].unique())
selected_country = st.sidebar.multiselect("Country", df['country'].unique())
date_range = st.sidebar.date_input(
    "Date Range", [df['dt'].min(), df['dt'].max()])

filtered = df.copy()
if selected_cat:
    filtered = filtered[filtered['category'].isin(selected_cat)]
if selected_country:
    filtered = filtered[filtered['country'].isin(selected_country)]
if len(date_range) == 2:
    filtered = filtered[(filtered['dt'].dt.date >= date_range[0]) & (
        filtered['dt'].dt.date <= date_range[1])]

col1, col2 = st.columns(2)
col1.metric("Net Delivered Revenue", f"${filtered['net_revenue'].sum():,.2f}")
col2.metric("Total Unique Orders", f"{filtered['order_id'].nunique():,}")

st.subheader("Daily Revenue Trend")
st.line_chart(filtered.groupby('dt')['net_revenue'].sum())

st.subheader("🤖 Live Forecast for Tomorrow")
if st.button("Predict"):
    # Calculate real database lags dynamically
    daily_totals = df.groupby('dt')['net_revenue'].sum()
    tomorrow = daily_totals.index.max() + datetime.timedelta(days=1)

    lag_1 = daily_totals.iloc[-1]
    lag_7 = daily_totals.iloc[-7] if len(daily_totals) >= 7 else lag_1

    # Load model directly to avoid localhost issues on Streamlit Cloud
    with open('data/model/forecast_model.pkl', 'rb') as f:
        model = pickle.load(f)

    pred = model.predict(pd.DataFrame([{
        "day_of_week": tomorrow.dayofweek, "month": tomorrow.month,
        "sales_lag_1": lag_1, "sales_lag_7": lag_7
    }]))[0]

    st.success(
        f"Forecast for {tomorrow.strftime('%Y-%m-%d')}: **${pred:,.2f}**")
