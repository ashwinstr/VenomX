# on_message.py

import os
import re
import traceback

import pyrogram
from pyrogram import Client as RClient, filters as flt
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from venom import Config
from venom.core.types import message
from venom.helpers import paste_it


class NewOnMessage(RClient):

    def new_on_message(self, filters: flt.Filter = None, group: int = -1):
        """ custom on message decorator """

        def wrapper(func):
            async def template(rc, rm: Message):
                if Config.PAUSE:
                    if bool(re.search(rf"^({Config.CMD_TRIGGER}|{Config.SUDO_TRIGGER})start$", rm.text)):
                        if rm.from_user.id != Config.OWNER_ID and rm.from_user.id not in Config.TRUSTED_SUDO_USERS:
                            return
                    else:
                        return
                new_message = message.MyMessage.parse(rc, rm)
                try:
                    await func(rc, new_message)
                except Exception as e:
                    error_ = traceback.format_exc().strip()
                    try:
                        await self.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                                text=f"###**MessageTraceback**###\n\n"
                                                     f"**PLUGIN:** `{func.__module__}`\n"
                                                     f"**FUNCTIONS:** `{func.__name__}`\n"
                                                     f"**ERROR:** `{e or None}`\n\n"
                                                     f"```{error_}```")
                    except MessageTooLong:
                        with open("traceback.txt", "w+") as tb:
                            tb.write(error_)
                        await self.send_document(chat_id=Config.LOG_CHANNEL_ID,
                                                 document="traceback.txt",
                                                 caption=f"###**MessageTraceback**###\n\n"
                                                         f"**PLUGIN:** `{func.__module__}`\n"
                                                         f"**FUNCTIONS:** `{func.__name__}`\n"
                                                         f"**ERROR:** `{e or None}`\n\n")
                        os.remove("traceback.txt")
                    link_ = await paste_it(error_)
                    await self.send_message(chat_id=rm.from_user.id,
                                            text=f"Something unexpected happened, send the below error to "
                                                 f"@UX_xplugin_support...\n<b>MessageTraceback:</b> [HERE]({link_})")

            self.add_handler(pyrogram.handlers.MessageHandler(template, filters), group)
            return template

        return wrapper
