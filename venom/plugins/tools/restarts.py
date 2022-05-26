# restarts.py

import time

from venom import venom, Config, MyMessage
from venom.helpers import plugin_name


HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}


###################################################################################################################################################################


HELP['commands'].append(
    {
        'command': 'restart',
        'flags': {
            '-h': 'hard restart',
        },
        'about': 'restart the bot',
        'syntax': '{tr}restart [optional flag]',
        'sudo': True
    }
)

@venom.trigger('restart')
async def rest_art(_, message: MyMessage):
    " restart the bot "
    if '-h' in message.flags:
        await message.edit("`Restart the bot [HARD] ...`")
        Config.HEROKU_APP.restart()
        return time.sleep(20)
    await message.edit("`Restarting the bot...`")
    await venom.restart()