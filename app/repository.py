from typing import Any, Dict, List, Optional

import asyncpg

from app.schemas import QueryRequest


async def save_request_result(
    pool: asyncpg.Pool,
    payload: QueryRequest,
    result: bool,
    status_code: int,
) -> Dict[str, Any]:
    sql = """
        INSERT INTO cadastral_requests (
            cadastral_number,
            latitude,
            longitude,
            external_result,
            external_status_code
        )
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, cadastral_number, latitude, longitude, external_result, created_at;
    """
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            sql,
            payload.cadastral_number,
            payload.latitude,
            payload.longitude,
            result,
            status_code,
        )
    return dict(row)


async def get_history(
    pool: asyncpg.Pool,
    cadastral_number: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    if cadastral_number is None:
        sql = """
            SELECT
                id,
                cadastral_number,
                latitude,
                longitude,
                external_result,
                external_status_code,
                created_at
            FROM cadastral_requests
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2;
        """
        args = (limit, offset)
    else:
        sql = """
            SELECT
                id,
                cadastral_number,
                latitude,
                longitude,
                external_result,
                external_status_code,
                created_at
            FROM cadastral_requests
            WHERE cadastral_number = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3;
        """
        args = (cadastral_number, limit, offset)

    async with pool.acquire() as connection:
        rows = await connection.fetch(sql, *args)
    return [dict(row) for row in rows]
