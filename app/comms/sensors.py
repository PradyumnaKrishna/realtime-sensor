"""
Sensor Communication Module.

Provides API to communicate with sensors and read data.
"""

import random

from typing import Protocol, runtime_checkable

from app.exceptions import InvalidSensor  # pylint: disable=unused-import


@runtime_checkable
class SensorProtocol(Protocol):
    """Sensor protocol."""

    name: str

    def read(self) -> float:
        """Read sensor value."""
        return 0.0

    def validate(self):
        """Validate sensor.

        Raises:
            InvalidSensor: If sensor is invalid.
        """


class RandomSensor(SensorProtocol):
    """Random sensor class."""

    name: str = "Random Sensor"

    def __init__(self, _max=100):
        self._max = _max

    def read(self) -> float:
        """Read a random value."""
        return random.random() * self._max

    def validate(self):
        """Validate sensor."""
