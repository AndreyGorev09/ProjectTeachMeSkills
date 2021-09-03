import os
from contextlib import asynccontextmanager
from typing import Any
from typing import AsyncIterator
from typing import Dict
from typing import List
from typing import Optional

import asyncpg

RowT = Dict[str, Any]
RowsT = List[RowT]

DATABASE_URL: str = os.getenv("DATABASE_URL", "").replace("postgresql", "postgres")


async def create_tables() -> None:
    sql = """
        CREATE TABLE IF NOT EXISTS numbers(
            name TEXT NOT NULL UNIQUE,
            n INTEGER NOT NULL DEFAULT 0
        );
    """

    await _execute_sql(sql)


async def drop_tables() -> None:
    sql = """
            DROP TABLE IF EXISTS numbers CASCADE;
        """

    await _execute_sql(sql)


async def get_number(name: str) -> Optional[int]:
    sql = """
        SELECT
            n
        FROM
            numbers
        WHERE
            name = $1
        ;
    """

    rows = await _execute_sql(sql, name)
    if not rows:
        return None

    assert len(rows) == 1

    return rows[0]["n"]


async def add_number(name: str, number: int) -> Optional[int]:
    sql = """
        INSERT INTO numbers(name, n)
        VALUES
            ($1, $2)
        ON CONFLICT (name) DO UPDATE 
        SET
            n = numbers.n + $2
        RETURNING
            numbers.n AS n
        ;
    """

    rows = await _execute_sql(sql, name, number)
    if not rows:
        return None

    assert len(rows) == 1

    return rows[0]["n"]


async def _execute_sql(sql: str, *args) -> RowsT:
    conn: asyncpg.Connection
    async with _connect_to_db() as conn:
        statement = await conn.prepare(sql)
        records = await statement.fetch(*args)

    rows = [dict(record) for record in records]

    return rows


@asynccontextmanager
async def _connect_to_db() -> AsyncIterator:
    connection: Optional[asyncpg.Connection] = None
    try:
        connection = await asyncpg.connect(DATABASE_URL)
        yield connection
    finally:
        if connection is not None:
            await connection.close()