import json
from datetime import datetime
from colorama import Fore, Fore

class _Config(object):
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        try:
            self.config = json.load(open('config.json'))
        except FileNotFoundError:
            default_config = {
                "bot_prefix": "$",
                "webhook_url": "",
                "bot_token": "",
                "auto_spread": False,
                "servers": { }
                }    
            with open("config.json","w") as f:
                f.write(json.dumps(default_config, indent=4))
            exit()


    #when item is set on dict, saves file.
    def __setitem__(self, key, value):
        self.config[key] = value
        with open("config.json","w") as f:
            f.write(json.dumps(self.config, indent=4))

    def __getitem__(self, key):
        return self.config[key]
        
        
config = _Config()

