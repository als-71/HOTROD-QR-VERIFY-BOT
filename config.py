import json

class _Config(dict):
    def __init__(self):
        self.load_config()
        
    def write(self):
        with open("config.json","w") as f:
            f.write(json.dumps(self, indent=4))

    def load_config(self):
        try:
            super().__init__(json.load(open('config.json')))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            default_config = {
                "bot_prefix": "$",
                "tokens_logged": 0,
                "webhook_url": "",
                "bot_token": "",
                "auto_spread": False,
                "servers": { }
                }    
            with open("config.json","w") as f:
                f.write(json.dumps(default_config, indent=4))
            exit()

global config
config = _Config()
