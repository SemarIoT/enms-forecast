import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import requests

post_url = 'https://iotlab-uns.com/smart-enms/api/daily-prediction'

def dailyPredict(manyDays):
    # Akuisisi data
    response = requests.get('https://iotlab-uns.com/smart-enms/api/daily-energy')
    data = response.json()
    
    today = datetime.now().date()
    lastSaturday = today - timedelta(days=today.weekday() + 2)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    #  Remove data before 1 Okt 24 because its not from datalogger and remove data after lastFriday
    df = df[(df['date'] >= '2024-10-01') & (df['date'] <= lastSaturday.strftime('%Y-%m-%d'))]

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['kwh'] = df['total']

    # Remove the first index (today) because its maybe not complete
    df = df[1:]

    df['dates'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    train = df.groupby('dates')['kwh'].sum().reset_index()
    train = train.set_index('dates')

    lastFriday = today - timedelta(days=today.weekday() + 3)
    predicted_days = pd.date_range(start=lastFriday, periods=manyDays+1, freq='d').strftime('%Y-%m-%d')[1:]
    
    # Exponential Smoothing
    es_model = ExponentialSmoothing(train['kwh'], seasonal='mul', trend='add', seasonal_periods=7)
    es_fit = es_model.fit()
    es_forecast = es_fit.forecast(steps=manyDays)

    forecast = []
    for i in range(len(predicted_days)):
        forecast.append({
            "predicted_day": predicted_days[i],
            "predicted_kwh": round(es_forecast[i],2),
        })
    response = requests.post(post_url, json=forecast)

    # Apakah POST request sukses
    if response.status_code == 200:
        return forecast
    else:
        return {"message": "Failed to send predictions to {post_url}"}
