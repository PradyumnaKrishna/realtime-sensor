"""
Exceptions module.
"""

class InvalidSensor(Exception):
    """Invalid sensor exception."""

    def __init__(self, message):
        super().__init__(message)
