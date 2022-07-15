from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel
from DiscordLib import MassDM


class Item(BaseModel):
    token: str
    username: str
    messages: list = []
    guild: int

app = FastAPI()

async def start_spreader(token, username, messages, guild):
    massdm = MassDM()
    await massdm.init(token, username, messages, guild)

    await massdm.message_dms()

    await massdm.message_friends()

    await massdm.message_guilds()

@app.post('/spread')
async def spread(item: Item, background_tasks: BackgroundTasks):
    background_tasks.add_task(start_spreader, item.token, item.username, item.messages, item.guild)
