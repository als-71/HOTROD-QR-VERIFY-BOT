import asyncpg
import asyncio

pool = None

async def connect():
    global pool

    #postgres://user:password@host:port/database?option=value
    dsn = 'postgres://postgres:1234@127.0.0.1:5432/disq'

    pool = await asyncpg.create_pool(dsn=dsn)

