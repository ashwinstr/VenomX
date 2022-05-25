# on_triggers.py

import os
from functools import wraps
import traceback
from typing import Any, Callable

import pyrogram
from pyrogram import filters, Client
from pyrogram.filters import Filter
from pyrogram.types import Message

from pyromod import listen

from venom import Config
from venom.core.types.message import MyMessage
from .. import filter
from ..command_manager import manager

_FUNC = Callable[['Message'], Any]

CURRENT_MODULE = ""

def owner_filter(cmd: str) -> Filter:
    " owner filters "
    filters_ = filters.regex(fr"^{Config.CMD_TRIGGER}{cmd}(\s(.|\n)*?)?$")\
        & filters.create(
            lambda _, __, m:
            (m.from_user and (m.from_user.id == Config.OWNER_ID))
        )
    return filters_

def sudo_filter(cmd: str) -> Filter:
    " sudo filters "
    filters_ = filters.regex(fr"^{Config.SUDO_TRIGGER}{cmd}(\s(.|\n)*?)?$")\
        & filters.create(
            lambda _, __, m:
            (m.from_user\
                and ((m.from_user.id in Config.TRUSTED_SUDO_USERS) or (m.from_user.id in Config.SUDO_USERS and cmd in Config.SUDO_CMD_LIST)))
        )
    return filters_

class MyDecorator(Client):
    _PYROFUNC = Callable[[_FUNC], _FUNC]

    def my_decorator(self, flt: 'filter.Filter', filters_=Filter, group: int = 0, **kwargs) -> 'MyDecorator._PYROFUNC':

        def inner(func: _FUNC) -> _FUNC:

            # preparing plugins and commands list
            global CURRENT_MODULE
            if func.__module__ != CURRENT_MODULE:
                manager.plugins.append(func.__module__)
            manager.commands.append(f"{func.__module__}.{flt.cmd}")
            CURRENT_MODULE = func.__module__

            filtered = filters_\
                and owner_filter(flt.cmd) | sudo_filter(flt.cmd)

            async def template(rc, rm) -> None:
                print(f"{rm.from_user.first_name} | {flt.cmd}")
                os.makedirs(Config.TEMP_PATH, exist_ok=True)
                new_message = MyMessage(rm)
                try:
                    await func(rc, new_message)
                except Exception as e:
                    await self.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                            text=f"### **TRACEBACK** ###\n\n"
                                                 f"**PLUGIN:** `{func.__module__}`\n"
                                                 f"**FUNCTIONS:** `{func.__name__}`\n"
                                                 f"**ERROR:** `{e or None}`\n\n"
                                                 f"```{traceback.format_exc().strip()}```")

            self.add_handler(pyrogram.handlers.MessageHandler(template, filtered), group)
            self.add_handler(pyrogram.handlers.EditedMessageHandler(template, filtered), group)
            return template
        return inner
