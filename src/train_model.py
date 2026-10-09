import pandas as pd
import sqlite3
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit


def train_forecast_model():
    conn = sqlite3.connect('data/processed/ecommerce.db')
    df = pd.read_sql(
        "SELECT DATE(order_timestamp) as dt, SUM(net_revenue) as daily_revenue FROM delivered_revenue GROUP BY 1", conn)
    conn.close()

    df['dt'] = pd.to_datetime(df['dt'])
    df = df.sort_values('dt').set_index('dt')

    df['day_of_week'] = df.index.dayofweek
    df['month'] = df.index.month
    df['sales_lag_1'] = df['daily_revenue'].shift(1)
    df['sales_lag_7'] = df['daily_revenue'].shift(7)
    df = df.dropna()

    features = ['day_of_week', 'month', 'sales_lag_1', 'sales_lag_7']
    X, y = df[features], df['daily_revenue']

    tscv = TimeSeriesSplit(n_splits=5)
    rf_maes, rf_mapes = [], []
    bl_lag1_maes, bl_lag7_maes, bl_mean_maes = [], [], []

    model = RandomForestRegressor(n_estimators=100, random_state=42)

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        model.fit(X_train, y_train)
        rf_pred = model.predict(X_test)

        rf_maes.append(mean_absolute_error(y_test, rf_pred))
        rf_mapes.append(mean_absolute_percentage_error(y_test, rf_pred))
        bl_lag1_maes.append(mean_absolute_error(y_test, X_test['sales_lag_1']))
        bl_lag7_maes.append(mean_absolute_error(y_test, X_test['sales_lag_7']))
        bl_mean_maes.append(mean_absolute_error(
            y_test, (X_test['sales_lag_1'] + X_test['sales_lag_7']) / 2))

    print("--- TimeSeriesSplit Backtest Results ---")
    print(
        f"Random Forest MAE: ${sum(rf_maes)/5:.0f} | MAPE: {sum(rf_mapes)/5*100:.1f}%")
    print(f"Naive Lag-1 MAE:   ${sum(bl_lag1_maes)/5:.0f}")
    print(f"Lag-7 MAE:         ${sum(bl_lag7_maes)/5:.0f}")
    print(f"Mean(Lag1,7) MAE:  ${sum(bl_mean_maes)/5:.0f}")

    # Retrain on full dataset for final serving
    model.fit(X, y)
    Path('data/model').mkdir(parents=True, exist_ok=True)
    with open('data/model/forecast_model.pkl', 'wb') as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    train_forecast_model()
