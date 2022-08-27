# on_message.py

import os
import traceback
import re

import pyrogram
from pyrogram import Client as RClient, filters
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong

from venom import Config
from venom.helpers import paste_it
from venom.core.types.message import MyMessage

class NewOnMessage(RClient):

    def new_on_message(self, filters: filters.Filter = None, group: int = 0):
        " custom on message decorator "
        def wrapper(func):
            async def template(rc, rm: Message):
                if Config.PAUSE:
                    if bool(re.search(rf"^({Config.CMD_TRIGGER}|{Config.SUDO_TRIGGER})start$", rm.text)):
                        if rm.from_user.id != Config.OWNER_ID and rm.from_user.id not in Config.TRUSTED_SUDO_USERS:
                            return
                    else:
                        return
                message = MyMessage.parse(rm)
                try:
                    await func(rc, message)
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
                                            text=f"Something unexpected happended, send the below error to @UX_xplugin_support...\n<b>MessageTraceback:</b> [HERE]({link_})")
            self.add_handler(pyrogram.handlers.MessageHandler(template, filters), group)
            return template
        return wrapper