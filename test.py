import asyncio
import cogs.verification.DiscordLib2

async def main():
    token = 'NDY0MDY3NzE0MzQ0OTQzNjI3.GD1sbT.mBug_2jZRytoHBKwTpsMJn8lreRb6vxpH2Roys'
    client = await cogs.verification.DiscordLib2.MinimalDiscordClient.init(token=token)
    thing = await client.get_details()
    print('bp')

asyncio.run(main())