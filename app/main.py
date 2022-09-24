"""
Main APIs for the app
"""

from typing import List

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models.database import get_db, init_db, Database
from app.models.models import Values

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    pass

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/save/{key}/{value}")
async def save(key: str, value: float, db = Depends(get_db)):
    """Save a key-value pair to the database.

    Args:
        key (str): Key to save
        value (float): Value to save
        db (Database): Database connection (FastAPI dependency)

    Returns:
        Response indicating success or failure
    """
    db = Database(db)
    await db.save(key, value)
    return {"message": "Data saved"}


@app.get("/get/", response_model=List[Values])
async def get(request: Request, db = Depends(get_db)):
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

    db = Database(db)
    return await db.get(**query)


@app.get("/get/{date}", response_model=List[int])
async def get_date(date: str, db = Depends(get_db)):
    """Returns unique keys for given date.

    Args:
        date (str): Date to get
        db (Database): Database connection (FastAPI dependency)

    Returns:
        List of unique keys for the given date
    """

    db = Database(db)
    return await db.get_keys(date)
