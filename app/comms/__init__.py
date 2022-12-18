"""
Communication Module.
"""

import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(settings.logger)

async def init_sensor():
    """Initializes and validates sensor."""

    sensor = settings.sensor

    if sensor:
        sensor.validate()
        logger.info("Sensor successfully validated.")
    else:
        logger.warning("No sensor found, live feature disabled.")
