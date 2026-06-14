from datetime import datetime

from pydantic import BaseModel, Field

from app.constants import (
    CADASTRAL_NUMBER_DESCRIPTION,
    CADASTRAL_NUMBER_EXAMPLE,
    CADASTRAL_NUMBER_MAX_LENGTH,
    CADASTRAL_NUMBER_MIN_LENGTH,
    CADASTRAL_NUMBER_PATTERN,
    LATITUDE_EXAMPLE,
    LONGITUDE_EXAMPLE,
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
)


class QueryRequest(BaseModel):
    cadastral_number: str = Field(
        min_length=CADASTRAL_NUMBER_MIN_LENGTH,
        max_length=CADASTRAL_NUMBER_MAX_LENGTH,
        pattern=CADASTRAL_NUMBER_PATTERN,
        examples=[CADASTRAL_NUMBER_EXAMPLE],
        description=CADASTRAL_NUMBER_DESCRIPTION,
    )
    latitude: float = Field(
        ge=MIN_LATITUDE,
        le=MAX_LATITUDE,
        examples=[LATITUDE_EXAMPLE],
    )
    longitude: float = Field(
        ge=MIN_LONGITUDE,
        le=MAX_LONGITUDE,
        examples=[LONGITUDE_EXAMPLE],
    )


class QueryResponse(BaseModel):
    id: int
    cadastral_number: str
    latitude: float
    longitude: float
    result: bool
    created_at: datetime


class HistoryItem(BaseModel):
    id: int
    cadastral_number: str
    latitude: float
    longitude: float
    result: bool
    external_status_code: int
    created_at: datetime


class ExternalResult(BaseModel):
    result: bool
