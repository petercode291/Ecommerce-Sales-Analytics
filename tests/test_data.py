import sqlite3
import pandas as pd

def test_no_future_dates():
    conn = sqlite3.connect('data/processed/ecommerce.db')
    df = pd.read_sql("SELECT MAX(order_timestamp) as max_date FROM orders", conn)
    conn.close()
    assert pd.to_datetime(df['max_date'].iloc[0]) <= pd.Timestamp('2026-09-30')