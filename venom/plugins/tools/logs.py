# logs.py

import asyncio

from pyrogram.enums import ParseMode
from pyrogram.errors import MessageDeleteForbidden

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name


HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}


########################################################################################################################


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
    """ get logs """
    try:
        await asyncio.gather(
            message.reply_document("logs/venom.log"),
            message.delete()
        )
    except MessageDeleteForbidden:
        pass
    except Exception as e:
        await message.edit(str(e))

########################################################################################################################

Config().help_formatter(
    name=__name__,
    command="logp",
    flags=None,
    usage="Send logs as printed message",
    syntax="{tr}logp [input number of lines]",
    sudo=True
)


@venom.trigger('logp')
async def print_logs(_, message: MyMessage):
    file_ = "logs/venom.log"
    lines = message.input_str
    if not lines or not lines.isdigit():
        lines = 10
    with open(file_, "r", encoding="utf-8") as f:
        log_ = f.readlines()
    log_ = "\n".join(log_[-int(lines):])
    await message.edit(
        f"<b>VenomX logs [{lines} lines]</b>\n\n<pre language=bash>{log_}</pre>",
        parse_mode=ParseMode.HTML
    )
