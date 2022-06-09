# loader.py

import time
import os
import importlib

from venom import venom, MyMessage, Config, Collection
from venom.helpers import plugin_name

HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}
RESTART = Collection.RESTART

####################################################################################################################################################################

HELP['commands'].append(
    {
        'command': 'load',
        'flags': None,
        'about': 'load plugin temporarily',
        'syntax': '{tr}load [reply to .py file]',
        'sudo': False
    }
)

@venom.trigger('load')
async def load_er(_, message: MyMessage):
    " load plugin temporarily "
    reply_ = message.replied
    if not reply_ or not reply_.document or not reply_.document.file_name.endswith(".py"):
        return await message.edit("`Reply to python plugin...`")
    await message.edit("`Trying to load...`")
    f_name = reply_.document.file_name
    plug_path = os.path.join(Config.TEMP_PATH, f_name)
    import_path = plug_path.replace("/", ".")[:-3]
    reload_ = False
    if os.path.exists(plug_path):
        os.remove(plug_path)
        reload_ = True
    await reply_.download(plug_path)
    try:
        importlib.import_module(import_path)
    except (SyntaxError, ImportError, NameError) as e:
        return await message.edit(f"`{e}`")
    msg = await message.edit("<b>Loaded</b> {},\nRestarting now.".format(f_name))
    if reload_:
        await RESTART.insert_one(
            {
                '_id': 'RESTART',
                'chat_id': msg.chat.id,
                'msg_id': msg.id,
                'start': time.time(),
                'msg': '<b>Reloaded temp plugin successfully.</b>\n<b>Time taken:</b> {} seconds.'
            }
        )
        await venom.restart()