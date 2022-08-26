# pause.py

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'security', 'commands': []}


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
    await message.edit("`Bot paused...`", del_in=3)