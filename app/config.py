"""
Configuration module.
"""


from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings

from app.comms.sensors import SensorProtocol, RandomSensor


class Settings(BaseSettings):
    """Settings model."""

    # Sensor
    sensor: Optional[SensorProtocol] = RandomSensor()

    # Logger (default is uvicorn)
    logger: str = "uvicorn"

    class Config:  # pylint: disable=too-few-public-methods
        """Config model."""
        env_file = ".env"


@lru_cache()
def get_settings():
    """Get settings."""
    return Settings()
