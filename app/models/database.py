"""
Module to provide API related to the database.
"""

from aiosqlite import connect

DATABASE_URL = "data.sqlite3"
TABLE = "SensorData"


async def get_db():
    """Get database connection."""
    async with connect(DATABASE_URL) as db:
        yield db


async def init_db():
    """Initialize database."""
    async with connect(DATABASE_URL) as db:
        await db.execute(f"CREATE TABLE IF NOT EXISTS {TABLE} "
            "(id INTEGER PRIMARY KEY, time DATETIME, key TEXT, value REAL)")
        await db.commit()


class Database:
    """Database class"""

    def __init__(self, db):
        """Initialize database."""
        self.db = db

    async def save(self, key, value):
        """Save data to database."""

        await self.db.execute(f"INSERT INTO {TABLE} (time, key, value) "
            "VALUES (datetime('now'), ?, ?)", (key, value))
        await self.db.commit()

    async def get(self, **kwargs):
        """Get data from database."""

        where = " AND ".join([f"{key} = ?" for key in kwargs])
        values = tuple(kwargs.values())

        # case for datetime having date.
        if "time" in kwargs:
            where = where.replace("time", "date(time)")

        # Database query.
        query = f"SELECT * FROM {TABLE} WHERE {where} ORDER BY time, key"
        async with self.db.execute(query, values) as cursor:
            data = await cursor.fetchall()

        return data
