# fedinfo.py

from pyrogram import filters as flt
from pyrogram.errors import YouBlockedUser
from pyrogram.enums import ParseMode

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name

help_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}
BOT_ = "MissRose_bot"

############################################################################################################################################

help_['commands'].append(
    {
        'command': 'fstat',
        'flags': None,
        'about': 'get fed stat from Rose',
        'syntax': '{tr}fstat [user id or reply to user]',
        'sudo': True
    }
)

@venom.trigger('fstat')
async def f_stat(_, message: MyMessage):
    " get fed statistic from Rose "
    user_ = message.input_str
    if not user_:
        reply_ = message.replied
        if not reply_:
            return await message.edit("`Give user id or reply to user to get fstat.`", del_in=5)
        user_ = reply_.from_user.id
    try:
        receive_ = await venom.ask(BOT_, f"/fstat {user_}", filters=flt.edit)
    except YouBlockedUser:
        return await message.edit("Unblock or start @MissRose_bot first.", del_in=3)
    await message.edit(receive_.text.html)  