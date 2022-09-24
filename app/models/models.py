"""
Pydantic models for the API
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class Values(BaseModel):
    """Values model."""
    key: str
    values: List[float]
    timestamps: List[datetime]
