import discord
import asyncio

from discord.ext import commands
import os






class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)


    async def on_ready(self):
        print('Bot online B)')


bot = Bot()


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
    await load_extensions()

    try:
        await bot.start(input('input token: '), bot=False)
    except discord.errors.LoginFailure:
        print(f'[Error] Failed to run bot. Check your token')
        input("Press enter to close the program... ")

if __name__ == "__main__":
    asyncio.run(main())
    


