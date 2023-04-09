from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import pandas as pd
import io
import matplotlib.pyplot as plt

from sqlalchemy.orm import Session

from models import Data
from database import SessionLocal

app = FastAPI()


class DataRequest(BaseModel):
    value: float


class DataResponse(BaseModel):
    id: int
    value: float
    timestamp: datetime


@app.post("/data")
def create_data(data_request: DataRequest):
    session = SessionLocal()

    data = Data(value=data_request.value, timestamp=datetime.now())

    session.add(data)
    session.commit()
    session.refresh(data)

    return {"id": data.id, "value": data.value, "timestamp": data.timestamp}


@app.get("/data/{last_hours}")
def get_data(last_hours: int):
    session = SessionLocal
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=last_hours)

    query = session.query(Data).filter(
        Data.timestamp >= start_time,
        Data.timestamp <= end_time).all()

    if not query:
        raise HTTPException(status_code=404, detail="Data not found")

    data = [{"id": item.id, "value": item.value,
             "timestamp": item.timestamp} for item in query]

    return data


@app.get('/plot')
def plot_data():
    session = SessionLocal()
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    query = session.query(Data).filter(
        Data.timestamp >= start_time,
        Data.timestamp <= end_time).all()

    if not query:
        raise HTTPException(status_code=404, detail="Data not found")

    df = pd.DataFrame([(item.timestamp, item.value)
                      for item in query], columns=["timestamp", "value"])
    df.set_index("timestamp", inplace=True)
    df = df.interpolate(method="cubic")

    fig, ax = plt.subplots()
    ax.plot(df.index, df["value"], '-', linewidth=2, markersize=1)
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")

    # устанавливаем количество точек на графике
    ax.locator_params(nbins=220, axis='x')

    buffer = io.BytesIO()

    fig.savefig(buffer, format="png")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")
