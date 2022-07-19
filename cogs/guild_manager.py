from discord.ext import commands
import asyncio
import json
import os
import discord
import utils

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

async def gather_overwrites(element):
    overwrites = {}
    for overwrite in element.overwrites:
        role_overwrites = dict(overwrite.permissions)
        overwrites[overwrite.name] = role_overwrites

        return overwrites

async def get_channels(ctx):
    categories = {}
    for category in ctx.guild.categories:
        channels = {}
        for channel in category.channels:
            if channel.overwrites:
                channel_overwrites = await gather_overwrites(channel)

            channels[channel.name] = {
                "last_message": None if channel.last_message == None else channel.last_message.content,
                "type": channel.type.name,
                "position": channel.position,
                "nsfw": channel.nsfw,
                "permissions_synced": channel.permissions_synced,
                "overwrites": None if channel.permissions_synced else channel_overwrites
            }

        categories[category.name] = channels
    return categories


async def get_roles(ctx):
    roles = {}
    for role in ctx.guild.roles:
        roles[role.name] = {
            "position": role.position,
            "colour": {
                "r": role.colour.r,
                "g": role.colour.g,
                "b": role.colour.b
            },
            "mentionable": role.mentionable,
            "permissions": dict(role.permissions)
        }
    return roles



class GuildManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def saveconfig(self, ctx: commands.Context, arg1):
     
        server = {
            "channels": await get_channels(ctx),
            "roles": await get_roles(ctx)
        }
        print(json.dumps(server, indent=4))

        # filename = "/server_configs/test.json"
        # os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(f"server_configs/{arg1}.json", "w") as f:
            f.write(json.dumps(server, indent=4))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def loadconfig(self, ctx: commands.Context):
        print('cock1')
        # config_path = os.path.join(utils.get_project_root, "/server_configs", f"cock.json")
        # config = await json.load('./server_configs/cock.json')
        print('coc2k')


    # @commands.command()
    # @commands.has_permissions(administrator=True)
    # async def loadserverconfig(self, ctx: commands.Context):

async def setup(bot):
    await bot.add_cog(GuildManagerCog(bot))