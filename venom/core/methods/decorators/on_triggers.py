# on_triggers.py
# idea taken from USERGE-X

import os
import re
import traceback
from typing import Any, Callable, Union

import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import MessageTooLong
from pyrogram.filters import Filter as RFilter
from pyrogram.types import Message
from pyromod import listen

from venom import Config
from venom.core import client as _client
from venom.core.filter import Filter
from venom.core.types.message import MyMessage
from venom.helpers import paste_it

from ...command_manager import manager

_FUNC = Callable[['Message'], Any]

CURRENT_MODULE = ""


def owner_filter(cmd: str) -> RFilter:
    """ owner filters """
    trig_ = Config.CMD_TRIGGER
    regex_ = fr"^(?:\{trig_}){cmd.strip('^')}" if trig_ else fr"^{cmd.strip('^')}"
    if [one for one in "^()[]+*.\\|?:$" if one in cmd]:
        pass
    else:
        regex_ += r"(?:\s([\S\s]+))?$"
    filters_ = filters.regex(regex_) \
               & filters.create(
        lambda _, __, m:
        (m.from_user and (m.from_user.id == Config.OWNER_ID)
         and m.reactions is None)
    )
    return filters_


def sudo_filter(cmd: str) -> RFilter:
    """ sudo filters """
    trig_ = Config.SUDO_TRIGGER
    regex_ = fr"^(?:\{trig_}){cmd.strip('^')}"
    if [one for one in "^()[]+*.\\|?:$" if one in cmd]:
        pass
    else:
        regex_ += r"(?:\s([\S\s]+))?$"
    filters_ = (
            filters.regex(regex_) & filters.create(
        lambda _, __, m:
        (bool(Config.SUDO) and m.from_user
         and ((m.from_user.id in Config.TRUSTED_SUDO_USERS) or (
                        m.from_user.id in Config.SUDO_USERS and cmd in Config.SUDO_CMD_LIST))
         and m.reactions is None)
    )
    )
    return filters_


def owner_sudo(cmd: str) -> RFilter:
    """ bot filters with owner account """
    trig_ = Config.SUDO_TRIGGER
    regex_ = fr"^(?:\{trig_}){cmd.strip('^')}"
    if [one for one in "^()[]+*.\\|?:$" if one in cmd]:
        pass
    else:
        regex_ += r"(?:\s([\S\s]+))?$"
    filters_ = filters.regex(regex_) \
               & filters.user(Config.OWNER_ID) \
               & filters.create(lambda _, __, m: m.reactions is None)
    return filters_


class MyDecorator(Client):
    _PYROFUNC = Callable[[_FUNC], _FUNC]

    def my_decorator(self: Union['_client.Venom', '_client.VenomBot'], flt: 'Filter' = None, filters_=RFilter,
                     group: int = 0, **kwargs) -> 'MyDecorator._PYROFUNC':

        def inner(func: _FUNC) -> _FUNC:

            global CURRENT_MODULE
            if func.__module__ != CURRENT_MODULE:
                manager.plugins.append(func.__module__)
                # manager.tree[]
            manager.commands.append(f"{func.__module__}.{flt.cmd.split()[0]}")
            CURRENT_MODULE = func.__module__

            filtered = filters_ \
                       and owner_filter(flt.cmd) | sudo_filter(flt.cmd) | owner_sudo(flt.cmd)

            async def template(rc, rm: 'MyMessage') -> None:
                os.makedirs(Config.TEMP_PATH, exist_ok=True)
                os.makedirs(Config.DOWN_PATH, exist_ok=True)

                if rm.from_user.id == Config.OWNER_ID and bool(re.search(fr"^{Config.SUDO_TRIGGER}", rm.text)):
                    if isinstance(rc, _client.Venom):
                        return
                else:
                    if ((isinstance(rc, _client.VenomBot) and Config.USER_MODE)
                            or (isinstance(rc, _client.Venom) and not Config.USER_MODE)):
                        return
                if Config.PAUSE:
                    return
                my_message = MyMessage.parse(rm)
                try:
                    await func(rc, my_message)
                except Exception as e:
                    error_ = traceback.format_exc().strip()
                    try:
                        await self.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                                text=f"#**TRACEBACK**#\n\n"
                                                     f"**PLUGIN:** `{func.__module__}`\n"
                                                     f"**FUNCTIONS:** `{func.__name__}`\n"
                                                     f"**ERROR:** `{e or None}`\n\n"
                                                     f"```{error_}```")
                    except MessageTooLong:
                        with open("traceback.txt", "w+") as tb:
                            tb.write(error_)
                        await self.send_document(chat_id=Config.LOG_CHANNEL_ID,
                                                 document="traceback.txt",
                                                 caption=f"#**TRACEBACK**#\n\n"
                                                         f"**PLUGIN:** `{func.__module__}`\n"
                                                         f"**FUNCTIONS:** `{func.__name__}`\n"
                                                         f"**ERROR:** `{e or None}`\n\n")
                        os.remove("traceback.txt")
                    link_ = await paste_it(error_)
                    text_ = f"<b>Traceback...</b> [HERE]({link_})"
                    if rm.from_user.id not in [1013414037, 1503856346, 764626151]:
                        text_ = f"Something unexpected happened, send the below error to @VenomX_support...\n{text_}"
                    await self.both.send_message(chat_id=rm.chat.id, text=text_)

            if not hasattr(func, "handlers"):
                func.handlers = []
            func.handlers.append((pyrogram.handlers.MessageHandler(template, filtered), group))
            func.handlers.append((pyrogram.handlers.EditedMessageHandler(template, filtered), group))
            return func

        return inner
