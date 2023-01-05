# restarts.py

import shutil
import asyncio

from venom import venom, Config, MyMessage, Collection
from venom.helpers import plugin_name, restart_msg

from ..devs.freezing import defrost_all

HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}


########################################################################################################################


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
    """ restart the bot """
    if "-reset" in message.flags:
        msg = await message.edit("`Restarting and resetting developments...`")
        await defrost_all()
        await Collection.FROZEN.drop()
        await restart_msg(msg, text=f"Restarted and reset the bot...")
        shutil.rmtree(Config.TEMP_PATH, ignore_errors=True)
        await Collection.TEMP_LOADED.drop()
        return asyncio.get_event_loop().create_task(venom.restart())
    action = "normally"
    if '-h' in message.flags:
        msg = await message.edit("`Restarting the bot [HARD] ...`")
        await Collection.FROZEN.drop()
        await restart_msg(msg=msg, text=msg.text)
        return await venom.restart()
    elif '-t' in message.flags:
        shutil.rmtree(Config.TEMP_PATH, ignore_errors=True)
        action = "and deleted temp path"
        await Collection.TEMP_LOADED.drop()
    elif '-d' in message.flags:
        shutil.rmtree(Config.DOWN_PATH, ignore_errors=True)
        action = "and emptied downloads path"
    msg = await message.edit(f"`Restarting the bot {action}...`")
    await restart_msg(msg=msg, text=f"Restarted the bot {action}...")    
    asyncio.get_event_loop().create_task(venom.restart())
