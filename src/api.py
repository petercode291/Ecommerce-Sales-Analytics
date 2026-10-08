from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pickle
import pandas as pd

app = FastAPI(title="Forecast API")

try:
    with open('data/model/forecast_model.pkl', 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    model = None

class ForecastRequest(BaseModel):
    month: int = Field(ge=1, le=12)
    day_of_week: int = Field(ge=0, le=6)
    sales_lag_1: float = Field(ge=0)
    sales_lag_7: float = Field(ge=0)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/forecast")
def predict_sales(data: ForecastRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model missing.")
    
    input_df = pd.DataFrame([{
        "day_of_week": data.day_of_week, "month": data.month,
        "sales_lag_1": data.sales_lag_1, "sales_lag_7": data.sales_lag_7
    }])
    
    return {"predicted_daily_revenue": round(model.predict(input_df)[0], 2)}