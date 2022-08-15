# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
# Ported to Venom by Ryuk.
# All rights reserved.

from venom import MyMessage, venom, Config
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}

##################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'del',
        'flags': None,
        'usage': 'delete replied message',
        'syntax': '{tr}del [reply to message]',
        'sudo': False
    }
)

@venom.trigger("del")
async def del_msg(_, message: MyMessage):
    msg_ids = [message.id]
    if message.reply_to_message:
        msg_ids.append(message.reply_to_message.id)
        await venom.delete_messages(message.chat.id, msg_ids)
    else:
        await message.edit("`Reply to message to delete...`", del_in=3)
