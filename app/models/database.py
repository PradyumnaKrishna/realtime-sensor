"""
Module to provide API related to the database.
"""

import itertools

from aiosqlite import connect

from app.config import get_settings


settings = get_settings()
DATABASE_URL = settings.database_url
TABLE = settings.database_table


async def get_db():
    """Get database connection."""
    async with connect(DATABASE_URL) as db:
        yield Database(db)


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
        if "date" in kwargs:
            where = where.replace("date", "date(time)")

        # Build Database query.
        query = f"SELECT * FROM {TABLE} "
        query += f"WHERE {where} " if where else ""
        query += "ORDER BY key, time"

        async with self.db.execute(query, values) as cursor:
            data = await cursor.fetchall()

        # extract values and time based on key in data.
        values = []
        for key, group in itertools.groupby(data, lambda x: x[2]):
            temp_dict = {
                "key": key,
                "values": [],
                "timestamps": [],
            }

            for row in group:
                temp_dict["values"].append(row[3])
                temp_dict["timestamps"].append(row[1])

            values.append(temp_dict)

        return values

    async def get_keys(self, date):
        """Get unique keys for a given date."""

        async with self.db.execute(f"SELECT DISTINCT key FROM {TABLE} "
            "WHERE date(time) = ?", (date,)) as cursor:
            data = await cursor.fetchall()

        return [row[0] for row in data]

    async def generate_key(self):
        """Generate a unique key for a sensor."""

        async with self.db.execute(f"SELECT DISTINCT key FROM {TABLE} "
            "WHERE date(time) = date('now')") as cursor:
            data = await cursor.fetchall()

        keys = [row[0] for row in data]

        if not keys:
            return "A"

        return chr(ord(max(keys)) + 1)
