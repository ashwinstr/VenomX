# restarts.py

import time

from venom import venom, Config, MyMessage, Collection
from venom.helpers import plugin_name

RESTART = Collection.RESTART

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
    await RESTART.drop()
    if '-h' in message.flags:
        msg = await message.edit("`Restart the bot [HARD] ...`")
        if Config.HEROKU_APP:
            await RESTART.insert_one(
                {
                    '_id': 'RESTART',
                    'chat_id': msg.chat.id,
                    'msg_id': msg.id,
                    'start': time.time()
                }
            )
            Config.HEROKU_APP.restart()
            return
        await msg.edit("`HEROKU_APP not found...`")
    msg = await message.edit("`Restarting the bot normally...`")
    await RESTART.insert_one(
        {
            '_id': 'RESTART',
            'chat_id': msg.chat.id,
            'msg_id': msg.id,
            'start': time.time()
        }
    )
    await venom.restart()