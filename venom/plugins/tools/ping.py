# ping.py

from datetime import datetime

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
    await message.edit("`Checking ping ...`")
    await message.edit("{} <b>PING</b> ---> <i>{} ms</i>".format(DOT_, (datetime.now() - start_).microseconds/1000))