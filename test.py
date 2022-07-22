import database
import asyncio

async def main():
    await database.connect()
    await database.pool.execute("INSERT INTO tokens VALUES (DEFAULT, 'ralph#2342', 'userid99999', 'tokeererhrhreh', 'email@cock.com', '+449292', '{ }', 'true', 'true', 'true')")

asyncio.run(main())