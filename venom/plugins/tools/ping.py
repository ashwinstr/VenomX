# ping.py

from datetime import datetime

from pyrogram.enums import ParseMode

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name

DOT_ = Config.BULLET_DOT
help_ = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}


##########################################################################################################################################


help_['commands'].append(
    {
        'command': 'ping',
        'flags': None,
        'about': 'check ping',
        'sudo': True
    }
)

@venom.trigger('ping')
async def pinger(_, message: MyMessage):
    " check ping "
    start_ = datetime.now()
    out_ = (
        "{dot} <b>PING</b> ---> <i>{ping} ms</i>\n"
        "{dot} <b>UPTIME</b> ---> <i>{uptime}</i>"
    )
    await message.edit("`Checking ping ...`")
    await message.edit(out_.format(dot=DOT_, ping=(datetime.now() - start_).microseconds/1000, uptime=venom.uptime), parse_mode=ParseMode.HTML)