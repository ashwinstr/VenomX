# dual_mode.py

import asyncio
import os

from venom import venom, Config, MyMessage, Collection
from venom.helpers import plugin_name
from ...core.methods.decorators.on_triggers import MyDecorator


HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'essents', 'commands': []}

async def _init() -> None:
    global trigger
    found = await Collection.TOGGLES.find_one({'_id': 'USER_MODE'})
    if found:
        Config.USER_MODE = found['switch']
    else:
        Config.USER_MODE = bool(Config.STRING_SESSION)

#######################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'mode',
        'flags': {
            '-c': 'check',
        },
        'usage': 'toggle mode [user/bot]',
        'syntax': '{tr}mode [optional flag]',
        'sudo': False
    }
)

@venom.trigger('mode')
async def dual_mode(_, message: MyMessage):
    " toggle mode [user/bot] "
    if '-c' in message.flags:
        switch_ = "USER" if Config.USER_MODE else "BOT"
        return await message.edit(f"Current mode: <b>{switch_}</b>", del_in=5)
    if not Config.STRING_SESSION:
        return await message.edit("`Can't change to USER mode without STRING_SESSION.`", del_in=3)
    if Config.USER_MODE:
        Config.USER_MODE = False
        mode_ = "BOT"
        client = venom.bot
    else:
        Config.USER_MODE = True
        mode_ = "USER"
        client = venom
    await Collection.TOGGLES.update_one(
        {'_id': 'USER_MODE'}, {'$set': {'switch': Config.USER_MODE}}, upsert=True
    )
    await message.edit(f"Mode changed to: <b>{mode_}</b>")
    MyDecorator.my_decorator(client)
