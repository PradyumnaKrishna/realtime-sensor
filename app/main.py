"""
Main APIs for the app.
"""

import logging

from datetime import datetime
from typing import List
from time import sleep

from fastapi import FastAPI, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from websockets.exceptions import ConnectionClosed

from app.comms import init_sensor
from app.config import get_settings
from app.exceptions import InvalidSensor
from app.models.database import get_db, init_db, Database
from app.models.models import Values, WSData, WSLog, WSResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

settings = get_settings()
logger = logging.getLogger(settings.logger)


@app.on_event("startup")
async def startup():
    await init_db()
    await init_sensor()

@app.on_event("shutdown")
async def shutdown():
    pass

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "live": settings.sensor is not None}
    )


@app.get("/check")
async def check():
    return {"message": "OK"}


@app.get("/save/{key}/{value}")
async def save(key: str, value: float, db: Database = Depends(get_db)):
    """Save a key-value pair to the database.

    Args:
        key (str): Key to save
        value (float): Value to save
        db (Database): Database connection (FastAPI dependency)

    Returns:
        Response indicating success or failure
    """

    await db.save(key, value)
    return {"message": "Data saved"}


@app.get("/get/", response_model=List[Values])
async def get(request: Request, db: Database = Depends(get_db)):
    """Returns all values for a given key or date.

    Args:
        request (Request): Request object
        db (Database): Database connection (FastAPI dependency)

    Parameters:
        key (str): Key to get
        date (str): Date to get

    Returns:
        List of values for the given key
    """

    query = dict(request.query_params)

    return await db.get(**query)


@app.get("/get/{date}", response_model=List[str])
async def get_keys(date: str, db: Database = Depends(get_db)):
    """Returns unique keys for given date.

    Args:
        date (str): Date to get
        db (Database): Database connection (FastAPI dependency)

    Returns:
        List of unique keys for the given date
    """

    return await db.get_keys(date)


def ws_log(level: int, message: str):
    """Generate a websocket log message.

    Args:
        level (str): Log level
        message (str): Log message
    """

    logger.log(level, message)
    data = WSLog(level=level, message=message)
    return WSResponse(type="log", data=data).dict()


@app.websocket("/live")
async def live(websocket: WebSocket, db: Database = Depends(get_db)):
    """Websocket for live data.

    Args:
        websocket (WebSocket): Websocket connection
        db (Database): Database connection (FastAPI dependency)
    """


    await websocket.accept()
    try:
        sensor = settings.sensor
        delay = settings.sensor_delay

        # Validate sensor.
        response = ws_log(
            20, f"Initializing Sensor: {sensor.name if sensor else sensor}"
        )
        await websocket.send_json(response)

        if sensor is None:
            response = ws_log(40, "No sensor configured.")
            await websocket.send_json(response)
            raise WebSocketDisconnect(code=1011, reason="No sensor configured.")

        try:
            sensor.validate()
        except InvalidSensor as e:
            response = ws_log(40, str(e))
            await websocket.send_json(response)
            raise WebSocketDisconnect(code=1011, reason=str(e)) from e

        # Generate new key to store the dataset.
        key = await db.generate_key()

        response = ws_log(20, f"Generated key: {key}")
        await websocket.send_json(response)

        while True:
            # Read data.
            value = sensor.read()

            data = WSData(key=key, value=value, timestamp=datetime.now().isoformat())
            await websocket.send_json(WSResponse(type="data", data=data).dict())

            # Save the data.
            await db.save(key, value)
            sleep(delay)

    except (WebSocketDisconnect, ConnectionClosed) as e:
        # Close the websocket (called by user or exception caused).
        await websocket.close(code=e.code, reason=e.reason)
