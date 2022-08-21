# on_triggers.py
# idea taken from USERGE-X

import os
import traceback
from typing import Any, Callable

import pyrogram
from pyrogram import filters, Client
from pyrogram.filters import Filter as RFilter
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong

from pyromod import listen

from venom import Config
from venom.core.types.message import MyMessage
from venom.core.filter import Filter
from venom.core import client as _client
from ...command_manager import manager

_FUNC = Callable[['Message'], Any]

CURRENT_MODULE = ""

def owner_filter(cmd: str) -> RFilter:
    " owner filters "
    trig_: str = "\." if Config.CMD_TRIGGER == "." else Config.CMD_TRIGGER
    filters_ = filters.regex(
        fr"^(?:\{trig_})({cmd.strip('^')})(\s(.|\n)*?)?$" if trig_ else fr"^{cmd.strip('^')}"
    )\
        & filters.create(
            lambda _, __, m:
            (m.from_user and (m.from_user.id == Config.OWNER_ID))
        )
    return filters_

def sudo_filter(cmd: str) -> RFilter:
    " sudo filters "
    trig_: str = "\." if Config.SUDO_TRIGGER == "." else Config.SUDO_TRIGGER
    filters_ = filters.regex(fr"^(?:\{trig_})({cmd})(\s(.|\n)*?)?$")\
        & filters.create(
            lambda _, __, m:
            (bool(Config.SUDO) and m.from_user\
                and ((m.from_user.id in Config.TRUSTED_SUDO_USERS) or (m.from_user.id in Config.SUDO_USERS and cmd in Config.SUDO_CMD_LIST)))
        )
    return filters_

class MyDecorator(Client):
    _PYROFUNC = Callable[[_FUNC], _FUNC]

    def my_decorator(self, flt: 'Filter', filters_ = RFilter, group: int = 0, **kwargs) -> 'MyDecorator._PYROFUNC':

        def inner(func: _FUNC) -> _FUNC:

            global CURRENT_MODULE
            if func.__module__ != CURRENT_MODULE:
                manager.plugins.append(func.__module__)
            manager.commands.append(f"{func.__module__}.{flt.cmd}")
            CURRENT_MODULE = func.__module__

            filtered = filters_\
                and owner_filter(flt.cmd) | sudo_filter(flt.cmd)

            async def template(rc, rm) -> None:
                os.makedirs(Config.TEMP_PATH, exist_ok=True)
                os.makedirs(Config.DOWN_PATH, exist_ok=True)
                if Config.USER_IS_SELF:
                    if isinstance(rc, _client.VenomBot):
                        return
                new_message = MyMessage(rm)
                try:
                    await func(rc, new_message)
                except Exception as e:
                    error_ = traceback.format_exc().strip()
                    try:
                        await self.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                            text=f"### **TRACEBACK** ###\n\n"
                                                 f"**PLUGIN:** `{func.__module__}`\n"
                                                 f"**FUNCTIONS:** `{func.__name__}`\n"
                                                 f"**ERROR:** `{e or None}`\n\n"
                                                 f"```{error_}```")
                    except MessageTooLong:
                        with open("traceback.txt", "w+") as tb:
                            tb.write(error_)
                        await self.send_document(chat_id=Config.LOG_CHANNEL_ID,
                                                document="traceback.txt",
                                                caption=f"### **TRACEBACK** ###\n\n"
                                                 f"**PLUGIN:** `{func.__module__}`\n"
                                                 f"**FUNCTIONS:** `{func.__name__}`\n"
                                                 f"**ERROR:** `{e or None}`\n\n")
                        os.remove("traceback.txt")

            self.add_handler(pyrogram.handlers.MessageHandler(template, filtered), group)
            self.add_handler(pyrogram.handlers.EditedMessageHandler(template, filtered), group)
            return template
        return inner
