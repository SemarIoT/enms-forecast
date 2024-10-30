import requests
from datetime import datetime
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

post_url = 'https://iotlab-uns.com/smart-enms/api/monthly-prediction'

def nextMonthPredict(manyMonths):
    # Akuisisi data
    response = requests.get('https://iotlab-uns.com/smart-enms/api/monthly-energy')
    data = response.json()

    manyMonthPredicted = manyMonths
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['kwh'] = df['total']

    # Remove the first index (current month) because its maybe not complete
    df = df[1:]

    # Group by month-year
    df['month'] = df['timestamp'].dt.strftime('%Y-%m')
    train = df.groupby('month')['kwh'].sum().reset_index()
    train = train.set_index('month')

    lastMonth = train.index[-1]

    # Name the predicted month
    predicted_month = pd.date_range(start=lastMonth, periods=manyMonths+1, freq='M').strftime('%Y-%m')[1:]

    # Exponential Smoothing
    es_model = ExponentialSmoothing(train['kwh'], seasonal='mul', trend='add', seasonal_periods=12)
    es_fit = es_model.fit()
    es_forecast = es_fit.forecast(steps=manyMonthPredicted)

    forecast = []
    for i in range(len(predicted_month)):
        forecast.append({
            "predicted_month": predicted_month[i],
            "predicted_kwh": round(es_forecast[i],2),
        })
    
    response = requests.post(post_url, json=forecast)

    # Apakah POST request sukses
    if response.status_code == 200:
        return forecast
    else:
        return {"message": "Failed to send predictions to {post_url}"}