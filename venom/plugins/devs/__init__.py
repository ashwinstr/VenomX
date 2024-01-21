# devs/__init__.py

import re

from pyrogram.enums import ParseMode

from venom import Config, get_devs, SecureConfig
from venom.core.types import MyMessage


async def init_func(message: MyMessage) -> str | bool | None:
    if not message:
        return None
    if not Config.DEVELOPER_MODE and (
        not message.from_user or message.from_user.id not in get_devs()
    ):
        await message.edit(
            f"`Secured command !!!`\n**Only DEVS can use this command or you can enable by using** "
            f"`{Config.CMD_TRIGGER}dev_mode true`**.**",
            parse_mode=ParseMode.MARKDOWN,
        )
        return None
    regex_ = re.search(
        rf"^({Config.CMD_TRIGGER}|{Config.SUDO_TRIGGER})(load)|(freeze)", message.text
    )
    if not bool(regex_):
        cmd = message.filtered_input
    else:
        cmd = True
    if not cmd:
        await message.edit("`Input not found...`")
        return None
    if isinstance(cmd, str) and "config.env" in cmd:
        await message.edit("`That's a dangerous operation! Not Permitted!`")
        return None
    return cmd
