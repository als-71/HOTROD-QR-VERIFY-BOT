import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run('OTk3NTQ0MTAxOTMzMjIzOTM2.GX492f.B2cI7ucFac78E-hx9Vj5F_aaSyYsemCNEaQ9J8')
