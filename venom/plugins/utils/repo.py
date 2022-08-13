# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from venom import Config, MyMessage, venom

help_ = Config.HELP[plugin_name(__name__)] = {'type': 'help', 'commands': []}


help_['commands'].append(
    {
        "about": "get repo link and details",
        "flags": {
            "-d": " Disables Link preview ",
            "-g": "MyGpack",
        },
    },
)


@venom.trigger(
    "repo"
)
async def see_repo(_,message: MyMessage):
    """see repo"""
    repo_ = (
        "[GPACK](https://github.com/VenomXuserbot/VenomX)"
        if "-g" in message.flags
        else f"[VenomX]({Config.UPSTREAM_REPO})"
    )
    output = f"• **repo** : {repo_}"
    if "-p" not in message.flags:
        await message.edit(output, dis_preview=True)
    else:
        await message.edit(output)
