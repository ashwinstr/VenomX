# pause.py

import asyncio

from pyrogram import filters

from venom import venom, MyMessage, Config, Collection
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'security', 'commands': []}

async def _init() -> None:
    found = await Collection.PAUSE.find_one({'_id': 'PAUSE'})
    if found:
        Config.PAUSE = found['paused']


##################################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'pause',
        'flags': None,
        'usage': 'pause the bot',
        'syntax': '{tr}pause',
        'sudo': False
    }
)

@venom.trigger('pause')
async def pause_it(_, message: MyMessage):
    " pause the bot "
    Config.PAUSE = True
    await asyncio.gather(
        Collection.PAUSE.update_one(
            {'_id': 'PAUSE'}, {'$set': {'paused': Config.PAUSE}}, upsert=True
        ),
        message.edit("`Bot paused...`", del_in=3)
    )

def owners(_, __, m):
    if m.from_user.id in Config.TRUSTED_SUDO_USERS or m.from_user.id == Config.OWNER_ID:
        return True
    return False

OWNERS = filters.create(owners)

@venom.on_message(
    filters.command(["start"], prefixes=[Config.CMD_TRIGGER, Config.SUDO_TRIGGER])
    & OWNERS,
    group=-1
)
async def start_(_, message: MyMessage):
    if not Config.PAUSE:
        return
    Config.PAUSE = False
    await asyncio.gather(
        Collection.PAUSE.update_one(
            {'_id': 'PAUSE'}, {'$set': {'paused': Config.PAUSE}}, upsert=True
        ),
        message.edit("`Bot started...`", del_in=3)
    )