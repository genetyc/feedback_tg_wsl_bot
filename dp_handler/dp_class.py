import asyncpg
from decouple import config
from asyncpg_lite import DatabaseManager


async def connect_to_db():
    data = config('DB_LOCAL')
    pool = await asyncpg.connect(data)
    return pool