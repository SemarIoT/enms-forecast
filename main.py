from fastapi import FastAPI
from monthly_predict import nextMonthPredict
from daily_predict import dailyPredict
import logging

app = FastAPI()

isDebug = False
if isDebug:
    post_url = 'http://127.0.0.1:8000/api/receive-forecast'
else:
    post_url = 'https://iotlab-uns.com/smart-enms/api/next-month-prediction'


@app.get("/")
def read_root():
    return {"What is this?": "Electricity Forecaster"}


@app.get("/v1/monthly-predict/{manyMonths}")
async def next_month_predict(manyMonths: int):
    try:
        result = nextMonthPredict(manyMonths)
        return result
    
    except Exception as e:
        logging.error("Error during prediction:", exc_info=True)
        raise 

@app.get("/v1/daily-predict/{manyDays}")
async def daily_predict(manyDays: int):
    try:
        result = dailyPredict(manyDays)
        return result
    
    except Exception as e:
        logging.error("Error during prediction:", exc_info=True)
        raise

