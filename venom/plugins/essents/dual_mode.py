# dual_mode.py

from venom import venom, Config, MyMessage, Collection
from venom.helpers import plugin_name
from venom.core import client as _client


HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'essents', 'commands': []}

async def _init() -> None:
    found = await Collection.TOGGLES.find_one({'_id': 'USER_MODE'})
    if found:
        Config.USER_MODE = found['switch']
    else:
        Config.USER_MODE = bool(Config.STRING_SESSION)

#######################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'mode',
        'flags': None,
        'usage': 'toggle mode [user/bot]',
        'syntax': '{tr}mode user/bot',
        'sudo': False
    }
)

@venom.trigger('mode')
async def dual_mode(_, message: MyMessage):
    " toggle mode [user/bot] "
    Config.FIRST = True
    input_ = message.input_str or ""
    if input_.lower() == "user":
        if Config.USER_MODE and isinstance(_, _client.VenomBot):
            return
        Config.USER_MODE = True
        await Collection.TOGGLES.update_one({'_id': 'USER_MODE'}, {'$set': {'switch': True}}, upsert=True)
        if Config.FIRST:
            Config.FIRST = False
            await message.edit("Mode set to: <b>USER</b>", del_in=5)
    elif input_.lower() == "bot":
        if not Config.USER_MODE and isinstance(_, _client.Venom):
            return
        Config.USER_MODE = False
        await Collection.TOGGLES.update_one({'_id': 'USER_MODE'}, {'$set': {'switch': False}}, upsert=True)
        if Config.FIRST:
            Config.FIRST = False
            await message.edit("Mode set to: <b>BOT</b>", del_in=5)
    else:
        mode_ = "USER" if Config.USER_MODE else "BOT"
        await message.edit(f"Current mode: <b>{mode_}</b>\nTo change, send `user` or `bot` as input.")
