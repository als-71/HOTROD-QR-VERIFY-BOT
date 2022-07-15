import asyncpg
import asyncio

pool = None

async def connect():
    global pool

    #postgres://user:password@host:port/database?option=value
    dsn = 'postgres://postgres:1234@127.0.0.1:5432/disq'

    pool = await asyncpg.create_pool(dsn=dsn)


async def main():
    await connect()
    await pool.execute("INSERT INTO tokens VALUES ('DAIWDU', 'ralph#3222', 'ralph@gmail.com', 0799959, true, false, true, true, 1)")


asyncio.run(main())
