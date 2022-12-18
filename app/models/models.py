"""
Pydantic models for the API
"""

from datetime import datetime
from typing import List, Literal, Union

from pydantic import BaseModel


class Values(BaseModel):
    """Values model."""
    key: str
    values: List[float]
    timestamps: List[datetime]


class WSData(BaseModel):
    """Websocket data response."""

    key: str
    value: float
    timestamp: str


class WSLog(BaseModel):
    """Websocket info model."""

    level: int
    message: str


class WSResponse(BaseModel):
    """Websocket response model."""

    type: Literal["data", "log"]
    data: Union[WSData, WSLog]
