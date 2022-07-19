import requests

data = {
    "message": "hello i am gay"
}

payload = {
    "name": "trketoer"
}

requests.post('https://discord.com/api/v9/guilds', json=payload)