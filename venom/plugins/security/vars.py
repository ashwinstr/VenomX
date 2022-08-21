# vars.py

from asyncio import TimeoutError, gather
from pyrogram import filters

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name
from .hide_vars import _DANG


HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'security', 'commands': []}
CHANNEL = venom.getCLogger(__name__)

##########################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'getvar',
        'flags': {
            '-f': 'forward to current chat '
        },
        'usage': 'get environment variable value in log channel',
        'syntax': '{tr}getvar [var name (case insensitive)]',
        'sudo': False
    }
)

@venom.trigger('getvar')
async def get_var(_, message: MyMessage):
    " get environment variable value in log channel "
    flags = message.flags
    input_ = message.filtered_input
    if not input_:
        return await message.edit("`Give var name as input...`", del_in=5)
    var_ = input_.upper()
    await message.edit(f"Getting var `{var_}`...")
    try:
        value_ = getattr(Config, str(var_))
    except AttributeError:
        return await message.edit(f"There's no var named <b>{var_}</b>...", del_in=5)
    except Exception as e:
        return await message.edit(f"<b>ERROR:</b>\n `{e}`", del_in=5)
    out_ = f"Var: `{var_}`\nValue: `{value_}`"
    if '-f' in flags:
        if var_ in _DANG:
            try:
                await message.ask(f"Var {var_} is dangerous to be exposed.\nAre you sure you want to send it in this chat? Send `Yes, I'm sure.` to confirm.", filters=(filters.regex(r"(?i)^Yes\, I\'m sure\.$") & filters.user(message.from_user.id)))
            except TimeoutError:
                return await message.edit("<b>Timeout!!!</b>\n`Terminating...`", del_in=5)
        return await gather(
            message.edit(out_),
            CHANNEL.log(f"Var <b>{var_}</b> sent to chat <b>{message.chat.title}</b>.")
        )
    await gather(
        CHANNEL.log(out_),
        message.edit(f"Var `{var_}` sent to log channel.")
    )