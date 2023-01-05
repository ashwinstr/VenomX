# pyname.py

import asyncio
import glob
import os
import re

from venom import venom, MyMessage, Config, plugin_name

help_ = Config.HELP[plugin_name(__name__)] = {'type': 'devs', 'commands': []}
DOT_ = Config.BULLET_DOT


async def _init() -> None:
    """ load non-py file list """
    Config.NON_PY_FILES.clear()
    sep = "\\" if "\\" in dir(__name__) else "/"
    total_list_ = glob.glob(f"venom{sep}plugins{sep}*{sep}*")
    for one in total_list_:
        search_ = re.search(r"(\w+)[\\/](\w+)$", one)
        plugin = search_.group(2) if search_ else ""
        if not plugin or plugin.startswith("__"):
            continue
        Config.NON_PY_FILES.update({plugin: one})

########################################################################################################################

help_['commands'].append(
    {
        'command': 'pyname',
        'flags': {
            '-l': 'list non-py files',
            '-r': 'reload list'
        },
        'usage': 'Rename python files to enable them',
        'syntax': '{tr}pyname [cmd|plugin name]',
        'sudo': False
    }
)


@venom.trigger('pyname')
async def python_rename(_, message: MyMessage):
    """ Rename python files to enable them """
    flags_ = message.flags
    await message.edit("`Searching...`")
    if "-l" in flags_:
        if Config.NON_PY_FILES:
            list_ = ""
            for one in Config.NON_PY_FILES.keys():
                list_ += f"{DOT_} {one}"
            out_ = f"<b>Unloaded plugins</b>: [<b>{len(Config.NON_PY_FILES.keys())}</b>]\n\n{list_}"
        else:
            out_ = "`No plugins are unloaded...`"
        return await message.edit(out_)
    elif "-r" in flags_:
        await _init()
        return await message.edit("`Non-loaded list reloaded...`")
    plug_ = message.filtered_input
    if plug_ not in Config.NON_PY_FILES.keys():
        return await message.edit(f"`No plugin named {plug_} is disabled...`", del_in=5)
    await message.edit(f"`Plugin {plug_} found.\nReloading...`")
    path_ = Config.NON_PY_FILES[plug_]
    os.rename(path_, f"{path_}.py")
    await message.edit(f"Plugin <b>{plug_}</b> reloaded.\n`Now restarting...`")
    asyncio.get_event_loop().create_task(venom.restart())
