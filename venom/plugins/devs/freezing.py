# freeze.py

import os
import asyncio

from venom import venom, MyMessage, Config, Collection, manager
from venom.helpers import plugin_name, restart_msg


HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'devs', 'commands': []}
FROZ_ = Collection.FROZEN
CHANNEL = venom.getCLogger(__name__)


############################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'freeze',
        'flags': None,
        'usage': 'disable plugin temporarily',
        'syntax': '{tr}freeze [command name]',
        'sudo': False
    }
)

@venom.trigger('freeze')
async def freezer_(_, message: MyMessage):
    " disable plugin temporarily "
    cmd_name = message.input_str
    if not cmd_name:
        return await message.edit("`Provide a plugin name or command name to disable...`", del_in=5)
    plug_loc = manager.cmd_plugin_loc(cmd_name)
    plug_name = manager.cmd_parent_plugin(cmd_name)
    if not plug_loc:
        return await message.edit(f"Input `{cmd_name}` is not valid command...", del_in=5)
    old_ = plug_loc + ".py"
    new_ = plug_loc
    found = await FROZ_.find_one({'_id': plug_name})
    if found:
        return await message.edit(f"The plugin <b>[{plug_name}]</b> is already frozen.", del_in=5)
    if os.path.exists(old_):
        os.rename(old_, new_)
        await FROZ_.insert_one({'_id': plug_name, "plug_loc": new_})
        restart_msg_ = await message.edit(f"Plugin <b>{plug_name}</b> got frozen temporarily.\n<b>Bot restarting...</b>")
        await CHANNEL.log(f"Plugin <b>{plug_name}</b> got frozen temporarily.\n<b>Bot restarting...</b>")
        text_ = f"Plugin <b>{plug_name}</b> frozen."
        await restart_msg(restart_msg_, text=text_)
        asyncio.get_event_loop().create_task(venom.restart())
    else:
        await message.edit(f"`The given plugin {plug_name} doesn't exist...`", del_in=5)

##############################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'defreeze',
        'flags': {
            '-all': 'defreeze all plugins'
        },
        'usage': 're-enable frozen plugins',
        'syntax': '{tr}defreeze [plugin name or optional flag]',
        'sudo': False
    }
)

@venom.trigger('defreeze')
async def defreezer_(_, message: MyMessage):
    " re-enable frozen plugin "
    if "-all" in message.flags:
        async for plug in FROZ_.find():
            old_ = plug["plug_loc"]
            new_ = f"{old_}.py"
            try:
                os.rename(old_, new_)
            except:
                pass
        await FROZ_.drop()
        msg_ = await message.edit("All frozen plugins are <b>re-enabled</b> now.\nRestarting bot...")
        await CHANNEL.log("All frozen plugins are <b>re-enabled</b>.")
        text_ = f"All plugins <b>defreezed</b>."
        await restart_msg(msg_, text=text_)
        asyncio.get_event_loop().create_task(venom.restart())
        return
    plug_name = message.filtered_input
    if not plug_name:
        return await message.edit("`Provide a plugin name to re-enable...`", del_in=5)
    found = await FROZ_.find_one({'_id': plug_name})
    if found:
        old_ = found["plug_loc"]
        new_ = f"{old_}.py"
        try:
            os.rename(old_, new_)
        except BaseException:
            return await message.edit(f"The plugin <b>{plug_name}</b> is already re-enabled.", del_in=5)
        await FROZ_.delete_one(found)
        out_ = f"Plugin <b>{plug_name}</b> got defrozen.\n<b>Bot restarting...</b>"
        msg_ = await message.edit(out_)
        await CHANNEL.log(out_)
        await restart_msg(msg_, text=f"Plugin {plug_name} re-enabled.")
        asyncio.get_event_loop().create_task(venom.restart())
    else:
        await message.edit(f"`The plugin {plug_name} is not frozen...`", del_in=5)

#########################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'frozen',
        'flags': None,
        'usage': 'list frozen plugins',
        'syntax': '{tr}forzen',
        'sudo': True
    }
)

@venom.trigger('frozen')
async def frozen_(_, message: MyMessage):
    " list frozen plugins "
    list_ = "The list of <b>frozen</b> plugins: [{}]\n\n"
    total = 0
    async for plug in FROZ_.find():
        total += 1
        plugin = plug['_id']
        list_ += f"• [{total}] `{plugin}`\n"
    if total == 0:
        return await message.edit("`No plugin is frozen at the moment.`", del_in=5)
    list_ = list_.format(total)
    await message.edit(list_)
