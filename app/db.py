from pathlib import Path

import asyncpg

from app.config import settings


async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=1,
        max_size=10
    )


async def run_migrations(pool: asyncpg.Pool) -> None:
    migration_path = (
        Path(__file__).resolve().parent.parent / "migrations" / "001_init.sql"
    )
    sql = migration_path.read_text(encoding="utf-8")
    async with pool.acquire() as connection:
        await connection.execute(sql)
