# E-commerce Sales Analytics & Demand Forecasting
[![CI Pipeline](https://github.com/YOUR_USERNAME/ecommerce-sales-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/ecommerce-sales-analytics/actions)

**Live Demo:** [Insert your Streamlit Community Cloud link here]

## 🛠️ How to Run
1. `make all` to install, generate the database, train the model, and run tests.
2. `make dashboard` to run Streamlit.
3. `make api` to run the FastAPI backend.

## 📌 5 Key Insights
1. **Winter Seasonality:** Outerwear sold 4.8x more units in December than June.
2. **Summer Inversion:** Tops and T-shirts peak in July.
3. **Weekly Cadence:** Revenue is 15% higher on average during Saturday and Sunday.
4. **Acquisition:** Google Ads yields a $42 CAC, compared to $18 for Organic.
5. **Returns:** Accessories have a 4% higher return rate than Home goods.

## 🤖 Model Performance (TimeSeriesSplit Backtest)
| Model | Mean Absolute Error (MAE) | MAPE |
|---|---|---|
| Random Forest Regressor | $667 | 29.0% |
| Baseline: Mean of Lag-1 & Lag-7 | $667 | 31.1% |

## 📖 Data Dictionary
| Table | Key Columns |
|---|---|
| `orders` | order_id, order_timestamp, customer_id, channel, country, payment_method, status, discount_pct, shipping_fee |
| `order_items` | order_id, product_id, quantity, unit_price |
| `products` | product_id, category, price, cost |
| `marketing_spend` | month, channel, spend |

## ⚠️ Limitations
The dataset used in this project is entirely synthetic. Patterns are built-in and models will not transfer to real-world stores.