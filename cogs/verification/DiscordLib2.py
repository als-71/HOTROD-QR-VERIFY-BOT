from math import perm
from typing import Dict
import ua_parser.user_agent_parser
import aiohttp
import base64
import json


class MinimalDiscordClient():
    @classmethod
    async def init(self, token):
        self = MinimalDiscordClient()

        self.BASEURL = 'https://discordapp.com/api/'
        self.headers = None
        self.session = None
        self.user = None

        parsed_ua = ua_parser.user_agent_parser.Parse('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36')
        locale='en-US'
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": '{},{};q=0.9'.format(locale, locale.split('-')[0]),
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Pragma": "no-cache",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="{0}", "Google Chrome";v="{0}"'.format(parsed_ua['user_agent']['major']),
            "Sec-Ch-Ua-Mobile": '?0',
            "Sec-Ch-Ua-Platform": '"{}"'.format(parsed_ua['os']['family']),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": parsed_ua['string'],
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": locale,
            "Origin": "https://discord.com",
            # "X-Super-Properties": base64.b64encode(json.dumps(self.__super_properties).encode()).decode("utf-8"),
            "Authorization": token,
        }

        headers.update({"X-Fingerprint": await self.get_xfingerprint()})
        # self.session.headers = self.headers
        self.session = aiohttp.ClientSession(headers=headers)

        return self

    
    async def get_xfingerprint(self):
        async with aiohttp.request("GET", f"{self.BASEURL}/experiments") as resp:
            data = await resp.json()
            return data.get('fingerprint')
            
    async def compute_base_permissions(self, guild):
        """
        MAKE SURE TO DESERIALIZE PERMS
        """
        if guild['is_owner']:
            return 'ALL'

        permissions = None

        for role in guild['roles']:
            if role['name'] == '@everyone':
                permissions = role['permissions']
        
        for role in guild: #placeholder make sure to replace this wiith user roles in guild
            permissions |= role['permissions']

        if permissions & 0x0000000000000008:
            return 'ALL'
        
        return permissions
    
    async def compute_overwrites(self, base_permissions, guild):
        if base_permissions & 0x0000000000000008:
            return 'ALL'

        permissions = base_permissions


    async def send_message(self, message, channel_id):
        async with self.session.request("GET", f"{self.BASEURL}/channels/{channel_id}/messages", json={'content': message}) as resp:
            try:
                data = await resp.json()
            except aiohttp.ContentTypeError: #cloudflare ratelimiting returns html
                return
        
        if resp.status == 200:
            return True
            
            

    async def open_dm(self, recipient):
        async with self.session.request("POST", f"https://discord.com/api/users/@me/channels",  json={"recipients": [recipient]}) as resp:
            data = await resp.json()
            return data.get('id')

    async def close_dm(self, dm_id):
        async with self.session.request("DELETE", f"https://discord.com/api/v8/channels/{dm_id}"):
            return

    async def get_guilds(self):
        async with self.session.request("GET", "https://discordapp.com/api/v6/users/@me/guilds") as resp:
            return await resp.json()

    async def get_guild_channels(self, guild_id):
        async with self.session.request("GET", f"https://discordapp.com/api/guilds/{guild_id}/channels") as resp:
            return await resp.json()


    async def get_dms(self):
        async with self.session.request("GET", f"https://discord.com/api/v8/users/@me/channels") as resp:
            return await resp.json()


    async def get_relationships(self):
        async with self.session.request("GET", f"https://discordapp.com/api/v6/users/@me/relationships") as resp:
            return await resp.json()

    async def send_friend_request(self, user):
        payload = {
            "username": user[0],
            "discriminator": user[1]
        }
        async with self.session.request("POST", "https://discord.com/api/v9/users/@me/relationships", json=payload) as resp:
            pass
    
    async def get_details(self):
        async with self.session.request("GET", "https://discordapp.com/api/v6/users/@me") as resp:
            data = await resp.json()
            if not data['phone']:
                data['phone'] = False
            return data
                
    async def get_relationships(self):
        async with self.session.request("GET", "https://discordapp.com/api/v6/users/@me/relationships") as resp:
            data = await resp.json()
            return len(data)

    async def get_guilds(self):
        async with self.session.request("GET", "https://discordapp.com/api/v6/users/@me/guilds?with_counts=true") as resp:
            return await resp.json()
        
    async def get_payment(self):
        async with self.session.request("GET", "https://discordapp.com/api/users/@me/billing/payment-sources") as resp:
            return await resp.json()

    async def get_roles(self, guild_id):
        async with self.session.request("GET", f"https://discordapp.com/api/guilds/{guild_id}/roles") as resp:
            return await resp.json()