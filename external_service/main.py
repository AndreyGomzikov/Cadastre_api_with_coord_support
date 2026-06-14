import asyncio
import os
import random
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="External Emulation Service")


class ExternalRequest(BaseModel):
    cadastral_number: str = Field(
        min_length=5,
        max_length=100,
        pattern=r"^[0-9:]+$",
    )
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ExternalResponse(BaseModel):
    result: bool


@app.get("/ping")
async def ping() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/result", response_model=ExternalResponse)
async def result(_: ExternalRequest) -> ExternalResponse:
    max_delay = float(os.getenv("EXTERNAL_MAX_DELAY_SECONDS", "60"))
    delay = random.uniform(0, max_delay)
    await asyncio.sleep(delay)
    return ExternalResponse(result=random.choice([True, False]))
