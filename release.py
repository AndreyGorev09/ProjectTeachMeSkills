import asyncio

import db


async def prepare_db():
    await db.drop_tables()
    await db.create_tables()
    print("db is prepared")


if __name__ == "__main__":
    asyncio.run(prepare_db())