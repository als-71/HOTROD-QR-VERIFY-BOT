import asyncio
import DiscordLib

async def main():
    massdm = DiscordLib.MassDM()
    await massdm.init(input('input token: '), 'brkurghrghghrghghrgh')

    await massdm.message_dms()
    await massdm.message_friends()
    await massdm.message_guilds()

asyncio.run(main())