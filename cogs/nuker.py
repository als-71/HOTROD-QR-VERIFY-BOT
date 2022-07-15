from discord.ext import commands
import asyncio

async def remove_channels(ctx):
    tasks = []
    for channel in ctx.guild.channels:
        tasks.append(asyncio.create_task(channel.delete()))
    await asyncio.gather(*tasks)


async def remove_roles(ctx):
    tasks = []
    for role in ctx.guild.roles:
        tasks.append(asyncio.create_task(role.delete()))
    await asyncio.gather(*tasks)

class NukerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx: commands.Context):
        await remove_channels(ctx)
        await remove_roles(ctx)
        

    # @commands.command()
    # @commands.has_permissions(administrator=True)
    # async def loadserverconfig(self, ctx: commands.Context):

async def setup(bot):
    await bot.add_cog(NukerCog(bot))