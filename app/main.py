import html
import random
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse

from app.config import settings
from app.constants import (
    ADMIN_DESCRIPTION,
    ADMIN_HEADER,
    ADMIN_PAGE_TITLE,
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CADASTRAL_NUMBER_MAX_LENGTH,
    CADASTRAL_NUMBER_MIN_LENGTH,
    CADASTRAL_NUMBER_PATTERN,
    DEFAULT_HISTORY_LIMIT,
    DEFAULT_HISTORY_OFFSET,
    MAX_HISTORY_LIMIT,
    MIN_HISTORY_LIMIT,
    MIN_HISTORY_OFFSET,
    PING_STATUS_KEY,
    PING_STATUS_OK,
)
from app.db import create_pool, run_migrations
from app.repository import get_history, save_request_result
from app.schemas import (
    ExternalResult,
    HistoryItem,
    QueryRequest,
    QueryResponse
)

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    fastapi_app.state.pool = await create_pool()
    await run_migrations(fastapi_app.state.pool)
    try:
        yield
    finally:
        await fastapi_app.state.pool.close()


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)


@app.get("/ping")
async def ping() -> Dict[str, str]:
    return {PING_STATUS_KEY: PING_STATUS_OK}


@app.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_201_CREATED
)
async def query(payload: QueryRequest, request: Request) -> QueryResponse:
    try:
        async with httpx.AsyncClient(
            timeout=settings.external_timeout_seconds
        ) as client:

            response = await client.post(
                settings.external_service_url,
                json=payload.model_dump(),
            )
        response.raise_for_status()
        external_data = ExternalResult.model_validate(response.json())
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External service error: {exc}",
        ) from exc

    row = await save_request_result(
        request.app.state.pool,
        payload,
        external_data.result,
        response.status_code,
    )
    return QueryResponse(
        id=row["id"],
        cadastral_number=row["cadastral_number"],
        latitude=row["latitude"],
        longitude=row["longitude"],
        result=row["external_result"],
        created_at=row["created_at"],
    )


@app.get("/history", response_model=List[HistoryItem])
async def history(
    request: Request,
    cadastral_number: Optional[str] = Query(
        default=None,
        min_length=CADASTRAL_NUMBER_MIN_LENGTH,
        max_length=CADASTRAL_NUMBER_MAX_LENGTH,
        pattern=CADASTRAL_NUMBER_PATTERN,
    ),
    limit: int = Query(
        default=DEFAULT_HISTORY_LIMIT,
        ge=MIN_HISTORY_LIMIT,
        le=MAX_HISTORY_LIMIT,
    ),
    offset: int = Query(
        default=DEFAULT_HISTORY_OFFSET,
        ge=MIN_HISTORY_OFFSET,
    ),
) -> List[HistoryItem]:
    rows = await get_history(
        request.app.state.pool,
        cadastral_number,
        limit,
        offset
    )
    return [
        HistoryItem(
            id=row["id"],
            cadastral_number=row["cadastral_number"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            result=row["external_result"],
            external_status_code=row["external_status_code"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@app.get(
    "/admin/requests",
    response_class=HTMLResponse,
    include_in_schema=True
)
async def admin_requests(
    request: Request,
    cadastral_number: Optional[str] = Query(
        default=None,
        min_length=CADASTRAL_NUMBER_MIN_LENGTH,
        max_length=CADASTRAL_NUMBER_MAX_LENGTH,
        pattern=CADASTRAL_NUMBER_PATTERN,
    ),
    limit: int = Query(
        default=DEFAULT_HISTORY_LIMIT,
        ge=MIN_HISTORY_LIMIT,
        le=MAX_HISTORY_LIMIT,
    ),
    offset: int = Query(
        default=DEFAULT_HISTORY_OFFSET,
        ge=MIN_HISTORY_OFFSET,
    ),
) -> HTMLResponse:
    rows = await get_history(
        request.app.state.pool,
        cadastral_number,
        limit,
        offset
    )
    table_rows = "".join(
        "<tr>"
        f"<td>{row['id']}</td>"
        f"<td>{html.escape(row['cadastral_number'])}</td>"
        f"<td>{row['latitude']}</td>"
        f"<td>{row['longitude']}</td>"
        f"<td>{row['external_result']}</td>"
        f"<td>{row['external_status_code']}</td>"
        f"<td>{row['created_at']}</td>"
        "</tr>"
        for row in rows
    )
    page = f"""
    <!doctype html>
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <title>{ADMIN_PAGE_TITLE}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 32px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>{ADMIN_HEADER}</h1>
        <p>{ADMIN_DESCRIPTION}</p>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Кадастровый номер</th>
                    <th>Широта</th>
                    <th>Долгота</th>
                    <th>Результат</th>
                    <th>HTTP status</th>
                    <th>Создано</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
    </body>
    </html>
    """
    return HTMLResponse(content=page)


@app.post("/result", response_model=ExternalResult)
async def result(_: QueryRequest) -> ExternalResult:
    return ExternalResult(result=random.choice([True, False]))
