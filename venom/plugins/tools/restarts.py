# restarts.py

import time
import shutil
import asyncio

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
            '-t': 'clear temp',
            '-d': 'clear downloads'
        },
        'about': 'restart the bot',
        'syntax': '{tr}restart [optional flag]',
        'sudo': True
    }
)

@venom.trigger('restart')
async def rest_art(_, message: MyMessage):
    " restart the bot "
    action = "normally"
    await RESTART.drop()
    if '-h' in message.flags:
        msg = await message.edit("`Restart the bot [HARD] ...`")
        if Config.HEROKU_APP:
            await RESTART.insert_one(
                {
                    '_id': 'RESTART',
                    'chat_id': msg.chat.id,
                    'msg_id': msg.id,
                    'start': time.time(),
                }
            )
            Config.HEROKU_APP.restart()
            return
        return await venom.restart()
    elif '-t' in message.flags:
        shutil.rmtree(Config.TEMP_PATH, ignore_errors=True)
        action = "and deleting temp path"
        await Collection.TEMP_LOADED.drop()
    elif '-d' in message.flags:
        shutil.rmtree(Config.DOWN_PATH, ignore_errors=True)
        action = "and emptying downloads path"
    msg = await message.edit(f"`Restarting the bot {action}...`")
    await RESTART.insert_one(
        {
            '_id': 'RESTART',
            'chat_id': msg.chat.id,
            'msg_id': msg.id,
            'start': time.time(),
        }
    )
    asyncio.get_event_loop().create_task(venom.restart())
