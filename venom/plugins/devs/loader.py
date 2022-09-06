# loader.py

import asyncio
import os
import importlib

from venom import venom, MyMessage, Config, Collection
from venom.helpers import plugin_name, restart_msg

HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}
RESTART = Collection.RESTART

####################################################################################################################################################################

HELP['commands'].append(
    {
        'command': 'load',
        'flags': {
            '-r': 'rename and load'
        },
        'about': 'load plugin temporarily',
        'syntax': '{tr}load [reply to .py file]',
        'sudo': False
    }
)

@venom.trigger('load')
async def load_er(_, message: MyMessage):
    " load plugin temporarily "
    reply_ = message.replied
    flags_ = message.flags
    if not reply_ or not reply_.document:
        return await message.edit("`Reply to python plugin...`")
    await message.edit("`Trying to load...`")
    f_name = reply_.document.file_name
    plug_path = os.path.join(Config.TEMP_PATH, f_name)
    import_path = plug_path.replace("/", ".")[:-3] if f_name.endswith('.py') else plug_path.replace("/", ".")
    if os.path.exists(plug_path):
        os.remove(plug_path)
    msg = "<b>Loaded</b> {},\nRestarting now.".format(f_name)
    down_ = await reply_.download(plug_path)
    try:
        if '-r' in flags_:
            new_path = f"{down_.rstrip('.py')}.py"
            os.rename(down_, new_path)
        importlib.import_module(import_path)
    except (SyntaxError, ImportError, NameError) as e:
        os.remove(down_)
        return await message.edit(f"`{e}`")
    load_conf = await message.edit(msg)
    text_ = f"<b>Reloaded temp plugin {f_name} successfully.</b>"
    await restart_msg(load_conf, text=text_)
    asyncio.get_event_loop().create_task(venom.restart())

##########################################################################################################################################################################

HELP['commands'].append(
    {
        'command': 'tload',
        'flags': None,
        'usage': 'load plugin using text message',
        'syntax': '{tr}tload [reply to text message] [plugin name]',
        'sudo': False
    }
)

@venom.trigger('tload')
async def text_load(_, message: MyMessage):
    " load using text message "
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to code message to load...`", del_in=5)
    path_ = "venom/plugins/temp/{}.py"
    plug_name = message.input_str
    if not plug_name:
        return await message.edit("`Plugin name not found...`", del_in=5)
    await message.edit("`Trying to load the temp plugin...`")
    code = reply_.text
    path_ = path_.format(plug_name)
    import_path = path_.replace("/", ".")[:-3]
    with open(path_, 'w+') as fn:
        fn.write(code)
    try:
        importlib.import_module(import_path)
    except (SyntaxError, ImportError, NameError) as e:
        os.remove(path_)
        return await message.edit(f"`{e}`")
    await message.edit(f"Loaded temp plugin <b>{plug_name}.py</b> successfully.")
