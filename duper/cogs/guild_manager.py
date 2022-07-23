from discord.ext import commands
import asyncio
import json
import os
import discord
from datetime import datetime


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
    thing = element.overwrites
    for overwrite in thing:
        if overwrite.managed:
            continue
        role_overwrites = dict(thing[overwrite])
        overwrites[overwrite.name] = role_overwrites
        
    return overwrites




async def get_channels(ctx: commands.Context):
    channels = {}
    for channel in ctx.guild.channels:
        if channel.type == discord.ChannelType.category:
            continue
        channel_overwrites = await gather_overwrites(channel)

        if channel.last_message_id:
            last_message = [message async for message in channel.history(limit=1)][0]
            last_message = last_message.content
        else:
            last_message = None
        channels[channel.name] = {
            "last_message": last_message,
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
    tasks = []
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

async def create_channels(ctx: commands.Context, guild, new_roles):
    categories = {}
    for category in guild['categories']:
        overwrites = {}

        for overwrite in guild['categories'][channel]['overwrites']:
            overwrites.update({
                new_roles[overwrite]: discord.PermissionOverwrite(**guild['categories'][channel]['overwrites'][overwrite])
            })
        new_category = await ctx.guild.create_category(name=category, position=guild['categories'][category].get('position'), overwrites=overwrites)
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
            new_channel = await ctx.guild.create_text_channel(**params)
        elif channel_type == 'voice':
            new_channel = await ctx.guild.create_voice_channel(**params)

        if guild['channels'][channel]['last_message']:
            await new_channel.send(guild['channels'][channel]['last_message'])


class GuildManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def saveconfig(self, ctx: commands.Context, arg1):
        server = {
            "categories": await get_categories(ctx),
            "channels": await get_channels(ctx),
            "roles": await get_roles(ctx)
        }

        filename = f"server_configs/{arg1}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as f:
            f.write(json.dumps(server, indent=4))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def loadconfig(self, ctx: commands.Context, arg1):
        await remove_channels(ctx)
        await remove_roles(ctx)


        guild = json.load(open(f'server_configs/{arg1}.json'))
        new_roles = await create_roles(ctx, guild)
        await create_channels(ctx, guild, new_roles)
      


async def setup(bot):
    await bot.add_cog(GuildManagerCog(bot))