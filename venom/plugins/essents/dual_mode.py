# dual_mode.py

from pyrogram.errors import PeerIdInvalid

from venom import venom, Config, MyMessage, Collection
from venom.core import client as _client
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'essents', 'commands': []}


async def _init() -> None:
    found = await Collection.TOGGLES.find_one({'_id': 'USER_MODE'})
    if found:
        Config.USER_MODE = found['switch']
    else:
        await Collection.TOGGLES.update_one(
            {
                '_id': 'USER_MODE',
                'switch': Config.USER_MODE
            }
        )

########################################################################################################################

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
    """ toggle mode [user/bot] """
    Config.FIRST = True
    input_ = message.input_str or ""
    if input_.lower() == "user":
        if not Config.VALID_STRING_SESSION:
            try:
                await venom.bot.send_message(
                    message.chat.id,
                    "Session string is <b>invalid</b> or <b>not found</b>\n<b>Can't change to user mode.</b>"
                )
            except BaseException as e:
                print(e)
            return
        if Config.USER_MODE and isinstance(_, _client.VenomBot):
            return
        if Config.FIRST:
            Config.FIRST = False
            try:
                await venom.send_message(message.chat.id, "Mode set to: <b>USER</b>")
            except PeerIdInvalid:
                return await message.edit("`User account need to be present in chat to change mode...`", del_in=5)
            Config.USER_MODE = True
            await Collection.TOGGLES.update_one({'_id': 'USER_MODE'}, {'$set': {'switch': True}}, upsert=True)
    elif input_.lower() == "bot":
        if not Config.USER_MODE and isinstance(_, _client.Venom):
            return
        if Config.FIRST:
            Config.FIRST = False
            try:
                await venom.bot.send_message(message.chat.id, "Mode set to: <b>BOT</b>")
            except PeerIdInvalid:
                return await message.edit("`Bot need to be present in chat to change mode...`", del_in=5)
            Config.USER_MODE = False
            await Collection.TOGGLES.update_one({'_id': 'USER_MODE'}, {'$set': {'switch': False}}, upsert=True)
    else:
        mode_ = "USER" if Config.USER_MODE else "BOT"
        await message.edit(f"Current mode: <b>{mode_}</b>\nTo change, send `user` or `bot` as input.")
