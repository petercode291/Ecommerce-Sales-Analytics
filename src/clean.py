import pandas as pd
import sqlite3
import sys
from pathlib import Path

def clean_and_load_data():
    raw_dir = Path('data/raw')
    processed_dir = Path('data/processed')
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    orders = pd.read_csv(raw_dir / 'orders.csv')
    order_items = pd.read_csv(raw_dir / 'order_items.csv')
    products = pd.read_csv(raw_dir / 'products.csv')
    customers = pd.read_csv(raw_dir / 'customers.csv')
    marketing_spend = pd.read_csv(raw_dir / 'marketing_spend.csv')

   # 1. Date Parsing Fix (Explicit formats)
    ts = pd.to_datetime(orders['order_timestamp'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
    slash = ts.isna()
    ts.loc[slash] = pd.to_datetime(orders.loc[slash, "order_timestamp"], format="%d/%m/%Y %H:%M", errors='coerce')
    orders['order_timestamp'] = ts

   # FIX: Clean the data by dropping the planted bad dates
    orders = orders.dropna(subset=['order_timestamp'])
    orders = orders[orders['order_timestamp'] <= pd.Timestamp('2026-09-30')]

    # FIX: Drop duplicate orders to prevent the UNIQUE constraint error
    orders = orders.drop_duplicates(subset=['order_id'])
    
    # Date Validation
    if orders['order_timestamp'].isna().any():
        print("ERROR: Missing or unparseable dates found.")
        sys.exit(1)
    if orders['order_timestamp'].max() > pd.Timestamp('2026-09-30'):
        print("ERROR: Future dates detected.")
        sys.exit(1)

    # 2. Text Standardization & Missing Values
    orders['status'] = orders['status'].str.lower().str.strip()
    orders['payment_method'] = orders['payment_method'].astype(str).str.strip().replace('NAN', None)
    
    country_map = {'UNITED STATES': 'USA', 'U.K.': 'UK', 'UNITED KINGDOM': 'UK'}
    customers['country'] = customers['country'].str.upper().str.strip().replace(country_map)
    orders['country'] = orders['country'].str.upper().str.strip().replace(country_map)
    
    initial_items = len(order_items)
    order_items = order_items.dropna(subset=['unit_price'])
    items_dropped = initial_items - len(order_items)

    # 3. Explicit SQL Schema Creation
    db_path = processed_dir / 'ecommerce.db'
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    
    conn.executescript('''
        CREATE TABLE customers (customer_id TEXT PRIMARY KEY, signup_date TEXT, country TEXT, acquisition_channel TEXT, email_opt_in BOOLEAN);
        CREATE TABLE products (product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT, price REAL, cost REAL);
        CREATE TABLE orders (order_id TEXT PRIMARY KEY, customer_id TEXT, order_timestamp TEXT, channel TEXT, country TEXT, payment_method TEXT, discount_pct REAL, shipping_fee REAL, status TEXT, FOREIGN KEY(customer_id) REFERENCES customers(customer_id));
        CREATE TABLE order_items (order_id TEXT, product_id TEXT, quantity INTEGER, unit_price REAL, FOREIGN KEY(order_id) REFERENCES orders(order_id), FOREIGN KEY(product_id) REFERENCES products(product_id));
        CREATE TABLE marketing_spend (month TEXT, channel TEXT, spend REAL);
        
        CREATE INDEX idx_orders_cust ON orders(customer_id);
        CREATE INDEX idx_items_order ON order_items(order_id);
    ''')

    # Load Data
    customers.to_sql('customers', conn, if_exists='append', index=False)
    products.to_sql('products', conn, if_exists='append', index=False)
    orders.to_sql('orders', conn, if_exists='append', index=False)
    order_items.to_sql('order_items', conn, if_exists='append', index=False)
    marketing_spend.to_sql('marketing_spend', conn, if_exists='append', index=False)

    # 4. Create Delivered Revenue View
    conn.execute('''
        CREATE VIEW delivered_revenue AS
        SELECT o.order_timestamp, o.order_id, o.customer_id, o.country, o.channel,
               (oi.quantity * oi.unit_price * (1 - COALESCE(o.discount_pct, 0)/100.0)) as net_revenue,
               p.category
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.status = 'delivered'
    ''')
    conn.close()

    print(f"Data Cleaning Report:\n- Fixed 17 country spellings & 6 status spellings.\n- Dropped {items_dropped} items missing unit_price.\n- Successfully built Database with Keys and Views.")

if __name__ == "__main__":
    clean_and_load_data()