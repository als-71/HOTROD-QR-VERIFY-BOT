from http.client import HTTPException
from unicodedata import category
from discord.ext import commands
import asyncio
import json
import os
import discord
import utils

async def remove_channels(ctx: commands.Context):
    tasks = []
    for channel in ctx.guild.channels:
        tasks.append(asyncio.create_task(channel.delete()))
    await asyncio.gather(*tasks)


async def remove_roles(ctx: commands.Context):
    tasks = []
    for role in ctx.guild.roles:
        if role == ctx.guild.default_role:
            continue
        elif role.managed:
            continue
        tasks.append(asyncio.create_task(role.delete()))
    await asyncio.gather(*tasks)

async def gather_overwrites(element : discord.channel):
    overwrites = {}
    for overwrite in element.overwrites:
        role_overwrites = dict(overwrite.permissions)
        overwrites[overwrite.name] = role_overwrites

        return overwrites

async def get_channels(ctx: commands.Context):
    channels = {}
    for channel in ctx.guild.channels:
        if channel.type == discord.ChannelType.category:
            continue
        # if channel.overwrites:
        channel_overwrites = await gather_overwrites(channel)

        channels[channel.name] = {
            "last_message": None if channel.last_message == None else channel.last_message.content,
            "type": channel.type.name,
            "position": channel.position,
            "category": channel.category.name if channel.category else None,
            "nsfw": channel.nsfw,
            "permissions_synced": channel.permissions_synced,
            "overwrites": None if channel.permissions_synced else channel_overwrites,
        }

    return channels

async def get_categories(ctx: commands.Context):
    categories = {}
    
    for category in ctx.guild.categories:
        # if category.overwrites:
        channel_overwrites = await gather_overwrites(category)

        categories[category.name] = {
            "position": category.position,
            "overwrites": channel_overwrites
            }

    return categories


async def get_roles(ctx: commands.Context):
    roles = {}
    for role in ctx.guild.roles:
        if role.managed: #if role is a bot role
            continue
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

async def create_roles(ctx: commands.Context, guild):
    roles = {}
    for role in guild['roles']:
        params = {
            'name': role,
            "mentionable": guild['roles'][role]['mentionable'],
            "colour": discord.Colour.from_rgb(**guild['roles'][role]['colour'])
        }
        if role == '@everyone':
            roles ['@everyone'] = ctx.guild.default_role
            await ctx.guild.default_role.edit(**params)
            continue

        new_role = await ctx.guild.create_role(**params)
        roles[role] = new_role
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
        await remove_channels(ctx)
        await remove_roles(ctx)

        categories = {}

        guild = json.load(open('server_configs/penile.json'))

        new_roles = await create_roles(ctx, guild)

        for category in guild['categories']:
            new_category = await ctx.guild.create_category(name=category, position=guild['categories'][category].get('position'))
            categories[category] = new_category
        for channel in guild['channels']:
            
            params = {
                "name": channel,
                "position": guild['channels'][channel].get('position')
                #category added conditionally as None is invalid for create_channel
            }
            if guild['channels'][channel]['overwrites']:
                overwrites = {}

                for overwrite in guild['channels'][channel]['overwrites']:
                    overwrites.update({
                        new_roles[overwrite]: discord.PermissionOverwrite(**guild['channels'][channel]['overwrites'][overwrite])
                    })
                params['overwrites'] = overwrites

            if guild['channels'][channel]['category']:
                if categories[guild['channels'][channel]['category']]:
                    params['category'] = categories[guild['channels'][channel]['category']] 

            channel_type = guild['channels'][channel].get('type')

            if channel_type == 'text':
                await ctx.guild.create_text_channel(**params)
            elif channel_type == 'voice':
                await ctx.guild.create_voice_channel(**params)




    # @commands.command()
    # @commands.has_permissions(administrator=True)
    # async def loadserverconfig(self, ctx: commands.Context):

async def setup(bot):
    await bot.add_cog(GuildManagerCog(bot))