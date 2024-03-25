# uploads.py

import asyncio

from venom import venom, MyMessage, Config, manager
from venom.helpers import plugin_name, paste_it


HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}

#####################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'pupload',
        'flags': {
            '-p': 'paste to pasty'
        },
        'usage': 'upload files from local',
        'syntax': '{tr}upload [command name]',
        'sudo': True
    }
)


@venom.trigger("pupload")
async def up_load(_, message: MyMessage):
    """ upload files from local """
    flags = message.flags
    cmd_name = message.filtered_input
    if not cmd_name:
        return await message.edit("`Give command name as input...`", del_in=5)
    loc_ = manager.cmd_plugin_loc(cmd_name)
    plug_ = manager.cmd_parent_plugin(cmd_name)
    action = " after pasting it" if '-p' in flags else ""
    if not loc_:
        return await message.edit(f"Input `{cmd_name}` is not a valid command !", del_in=5)
    process_ = await message.edit(f"`Uploading plugin {plug_}{action}...`")
    if '-p' in flags:
        with open(f"{loc_}.py", "r") as doc_:
            content_ = doc_.read()
        link_ = await paste_it(content_)
        await process_.edit(f"Content of plugin <b>{plug_}</b> pasted <b>[HERE]({link_})</b>.")
    else:
        await asyncio.gather(
            message.reply_document(f"{loc_}.py"),
            process_.delete()
        )