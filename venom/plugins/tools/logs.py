# logs.py

import asyncio

from pyrogram.errors import MessageDeleteForbidden

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name


HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}


################################################################################################################################################


HELP['commands'].append(
    {
        'command': 'logs',
        'flags': None,
        'about': 'check logs',
        'syntax': '{tr}logs',
        'sudo': True
    }
)

@venom.trigger('logs')
async def get_logs(_, message: MyMessage):
    " get logs "
    try:
        await asyncio.gather(
            message.reply_document("logs/venom.log"),
            message.delete()
        )
    except MessageDeleteForbidden:
        pass
    except Exception as e:
        await message.edit(e)

