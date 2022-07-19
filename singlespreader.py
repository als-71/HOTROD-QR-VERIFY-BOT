import asyncio
import aiohttp
from colorama import Fore

class MassDM:
    async def init(self, token, name):
        self.token = token
        self.headers = await self.get_headers(token)
        self.name = name #for printing
        self.msg_index = 0


    async def get_headers(self, token, content_type="application/json"):
        headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",      
            }
        if token:
            headers.update({"Authorization": token})
        return headers
    
    async def get_guilds(self):
        async with aiohttp.request("GET", "https://discordapp.com/api/v6/users/@me/guilds", headers=self.headers) as resp:
            return await resp.json()

    async def get_guild_channels(self, guild_id):
        async with aiohttp.request("GET", f"https://discordapp.com/api/guilds/{guild_id}/channels", headers=self.headers) as resp:
            return await resp.json()


    async def get_dms(self):
        async with aiohttp.request("GET", f"https://discord.com/api/v8/users/@me/channels", headers=self.headers) as resp:
            return await resp.json()


    async def get_relationships(self):
        async with aiohttp.request("GET", f"https://discordapp.com/api/v6/users/@me/relationships", headers=self.headers) as resp:
            return await resp.json()
        
    async def update_status(self, message):
        payload = {
            "bio": message
        }       
        async with aiohttp.request("PATCH", f"https://discord.com/api/v9/users/@me", json=payload, headers=self.headers) as resp:
            return await resp.json()


    
    async def message_channel(self, channel_id, message=None):
        for _ in range(5):


            payload = {
                "content": "https://discord.gg/gmYWznaMAY"
            }
            async with aiohttp.request("POST", f"https://discordapp.com/api/channels/{channel_id}/messages", json=payload, headers=self.headers) as resp:
                data = await resp.json()
                if resp.status == 401: #
                    break
            
                if resp.status == 403:
                    break

                if 'You need to verify your account in order to perform this action.' in data:
                    return 'locked'

                if 'captcha_key' in data:
                    return "captcha"

                if 'retry_after' in data:
                    if data['retry_after']/1000 > 10:
                        return "rate_limit"
                    await asyncio.sleep(data['retry_after']/1000)

                if 'Message was blocked by automatic moderation' in data:
                    return 'moderation'
                if 'code' in data:
                    if data['code'] == 50007:
                        break
                
                if 'Missing Access' in data:
                    break
                
                if 'id' in data:
                    break
            

                


    async def open_dm(self, recipient):
        payload = {"recipients": [recipient]} #[] because its an array just only 1 element, this endpoint designed to support multiple people
        async with aiohttp.request("POST", f"https://discord.com/api/users/@me/channels", headers=self.headers, json=payload) as resp:
            data = await resp.json()
            return data['id']
    
    async def close_dm(self, dm_id):
        async with aiohttp.request("DELETE", f"https://discord.com/api/v8/channels/{dm_id}", headers=self.headers):
            return

    async def message_friends(self):
        for relationship in await self.get_relationships():
            if not 'type' in relationship: #check if any relationships
                return

            if relationship['type'] == 1:
                dm_id = await self.open_dm(relationship['id'])
                resp = await self.message_channel(dm_id)
                if resp == "captcha":
                    return
                if resp == "rate_limit":
                    return
                if resp == "locked":
                    return
                if resp == "moderation":
                    return
                await self.close_dm(dm_id)
                print(f'{Fore.BLUE}[MassDM] [USER:{self.name}] [FRIEND:{relationship["user"]["username"]}#{relationship["user"]["discriminator"]}]')


    
    async def message_dms(self):
        for dm in await self.get_dms():
            if not 'id' in dm: # check if any dms
                return

            resp = await self.message_channel(dm['id'])
            if resp == "captcha":
                return
            if resp == "rate_limit":
                return
            if resp == "locked":
                return
            if resp == "moderation":
                return
            await self.close_dm(dm['id'])
            print(f'{Fore.BLUE}[MassDM] [USER:{self.name}] [DM:{len(dm["recipients"])}]')



    async def message_guilds(self):

        for guild in await self.get_guilds():
            if not 'id' in guild: #check if any guilds
                return

            # self.update_status(random.choice(config.config["auto_spread"]["messages"]))

            for channel in await self.get_guild_channels(guild['id']):
                if not 'type' in channel: #check if any channels
                    return

                if channel['type'] == 0:
                    resp = await self.message_channel(channel['id'])
                    if resp == "captcha":
                        return
                    if resp == "rate_limit":
                        return
                    if resp == "locked":
                        return
                    if resp == "moderation":
                        return
                    print(f'{Fore.BLUE}[MassDM] [USER:{self.name}] [GUILD:{guild["name"]}] [CHANNEL:{channel["name"]}]')

    

async def main():
    massdm = MassDM()
    await massdm.init('ODk5NzE4MTA0ODAyODA3ODM5.Gr_x4j.niYSV9isbTeXWAOhrD1IPwiPIgZP8L2tG0oAWc', 'zowkycunt')

    # await massdm.update_status(random.choice(config.config["auto_spread"]["messages"]))

    await massdm.message_dms()

    await massdm.message_friends()

    await massdm.message_guilds()

asyncio.run(main())