from unicodedata import category
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
    channels = {}
    for channel in ctx.guild.channels:
        if channel.type == discord.ChannelType.category:
            continue
        if channel.overwrites:
            channel_overwrites = await gather_overwrites(channel)

        channels[channel.name] = {
            "last_message": None if channel.last_message == None else channel.last_message.content,
            "type": channel.type.name,
            "position": channel.position,
            "nsfw": channel.nsfw,
            "permissions_synced": channel.permissions_synced,
            "overwrites": None if channel.permissions_synced else channel_overwrites,
            "category": channel.category.name
        }

    return channels

async def get_categories(ctx):
    categories = {}
    
    for category in ctx.guild.categories:
        if category.overwrites:
            channel_overwrites = await gather_overwrites(category)

        categories[category.name] = {
            "position": category.position,
            "overwrites": channel_overwrites
            }

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
        print('save')
        server = {
            "categories": await get_categories(ctx),
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
        categories = []
        # config_path = os.path.join(utils.get_project_root, "/server_configs", f"cock.json")
        guild = json.load(open('server_configs\hhhhhhhhh.json'))
        print('coc2k')
        for category in guild['categories']:
            print(guild['categories'][category].get('name'))
            new_category = await ctx.guild.create_category(name=category, position=guild['categories'][category].get('position'))
            categories.append(new_category)
        for channel in guild['channels']:
            if guild['channels'][channel].get('type') == 'text':
                await ctx.guild.create_text_channel(name=channel, position= guild['channels'][category].get('position'), 
                                                    category=guild['channels'][category].get('category'))


    # @commands.command()
    # @commands.has_permissions(administrator=True)
    # async def loadserverconfig(self, ctx: commands.Context):

async def setup(bot):
    await bot.add_cog(GuildManagerCog(bot))