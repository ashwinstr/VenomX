# loader.py

import importlib
import os
import traceback
import sys

from venom import venom, MyMessage, Config, Collection
from venom.helpers import plugin_name
from . import init_func

HELP = Config.HELP[plugin_name(__name__)] = {'type': 'devs', 'commands': []}
RESTART = Collection.RESTART

########################################################################################################################

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
    """ load using text message """
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

#############################################################################################

HELP['commands'].append(
    {
        'command': 'load',
        'flags': None,
        'usage': 'new plugin loader',
        'syntax': '{tr}load [reply to plugin file]',
        'sudo': False
    }
)


@venom.trigger('load')
async def loader(_, message: MyMessage):
    """ new loader plugin """
    secure_ = await init_func(message)
    if not secure_:
        return await message.edit("**DANGEROUS PLUGIN...** `ABORTING.`", del_in=5)
    reply_ = message.replied
    if not reply_ \
        or not reply_.document \
            or not reply_.document.file_name.endswith(".py"):
        return await message.edit("`Reply to plugin file...`", del_in=5)
    await message.edit("`Loading...`")
    file_name = reply_.document.file_name
    reload_ = False
    action = "loaded"
    path_ = f"venom/plugins/temp/{file_name}"
    if os.path.exists(path_):
        reload_ = True
        action = "reloaded"
        os.remove(path_)
    import_path_ = f"venom.plugins.temp.{file_name.split('.')[0]}"
    sys.modules.pop(import_path_, None) if reload_ else None
    await reply_.download(path_)
    try:
        module_ = importlib.import_module(import_path_)
        importlib.reload(module_)
    except ImportError as i_e:
        print(i_e)
        return await message.edit(traceback.format_exc())
    await message.edit(f"Temp plugin **{file_name.split('.')[0]}** {action}.")
