"""
Main APIs for the app
"""

from fastapi import FastAPI, Depends

from app.models.database import get_db, init_db, Database

app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    pass

@app.get("/")
async def root():
    return {"message": "Hello World"}


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


@app.get("/get/")
async def get(key: str = "", date: str = "", db = Depends(get_db)):
    """Returns all values for a given key or date.

    Args:
        key (str, optional): Key to get. Defaults to "".
        date (str, optional): Date to get. Defaults to "".
        db (Database): Database connection (FastAPI dependency)

    Returns:
        List of values for the given key
    """
    db = Database(db)

    if key and date:
        return await db.get(key=key, time=date)
    if key:
        return await db.get(key=key)
    if date:
        return await db.get(time=date)

    return await db.get()
