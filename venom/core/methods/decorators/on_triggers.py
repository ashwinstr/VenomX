# on_triggers.py
# idea taken from USERGE-X

import os
import re
import traceback
import asyncio
from typing import Any, Callable, Union, Dict

from pyrogram import Client, filters  # pyright:ignore
from pyrogram.errors import MessageTooLong
from pyrogram.filters import Filter as RawFilter
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler, EditedMessageHandler  # pyright:ignore
from pyrogram import StopPropagation, ContinuePropagation
from venom import Config
from venom.core import client as _client
from venom.core.filter import Filtered
from venom.core.types import message
from venom.helpers import paste_it
from ...command_manager import manager  # pylint:disable=E0402

_FUNC = Callable[[Client, Message], Any]


_CURRENT_MODULE = ""


class _EditableMessageDict(dict):
    """Manual check"""

    def __init__(self):
        self.dicts_: Dict[int, Dict[int, str]] = {}
        super().__init__()


_editable_message = _EditableMessageDict()


def reactions_not_found(msg: Union["message.MyMessage", "Message"]) -> bool:
    """reactions filtered out"""
    if not _client_check(msg._client):
        return False
    dicts_ = _editable_message.dicts_
    chats_ = dicts_.keys()
    if msg.chat.id in chats_:
        chat_ = dicts_[msg.chat.id]
        msgs_ = chat_.keys()
        if msg.id in msgs_:
            msg_text = chat_[msg.id]
            if msg_text != msg.text:
                chat_[msg.id] = msg.text
                return True
        else:
            if len(chat_) >= 5:
                first_msg = list(chat_.keys())[0]
                if msg.id > first_msg:
                    chat_.pop(first_msg)
                    chat_[msg.id] = msg.text
                    return True
            else:
                chat_[msg.id] = msg.text
                return True
        return False
    else:
        chat = dicts_[msg.chat.id] = {}
        chat[msg.id] = msg.text
        return True


def _client_check(client: Union["_client.Venom", "_client.VenomBot", "Client"]) -> bool:
    """filter in current client mode"""
    if isinstance(client, _client.VenomBot) and Config.USER_MODE:
        return False
    elif isinstance(client, _client.Venom) and not Config.USER_MODE:
        return False
    else:
        return True


def _owner_filter(cmd: str) -> RawFilter:
    """owner filters"""
    trig_ = Config.CMD_TRIGGER
    regex_ = rf"^(?:\{trig_}){cmd.strip('^')}" if trig_ else rf"^{cmd.strip('^')}"
    if [one for one in "^()[]+*.\\|?:$" if one in cmd]:
        pass
    else:
        regex_ += r"(?:\s([\S\s]+))?$"
    filters_ = filters.regex(regex_) & filters.create(
        lambda _, __, m: m.from_user
        and (m.from_user.id == Config.OWNER_ID)
        and reactions_not_found(m)
    )
    return filters_


def _sudo_filter(cmd: str) -> RawFilter:
    """sudo filters"""
    trig_ = Config.SUDO_TRIGGER
    regex_ = rf"^(?:\{trig_}){cmd.strip('^')}"
    if [one for one in "^()[]+*.\\|?:$" if one in cmd]:
        pass
    else:
        regex_ += r"(?:\s([\S\s]+))?$"
    filters_ = filters.regex(regex_) & filters.create(
        lambda _, __, m: (
            bool(Config.SUDO)
            and m.from_user
            and (
                (m.from_user.id in Config.TRUSTED_SUDO_USERS)
                or (m.from_user.id in Config.SUDO_USERS and cmd in Config.SUDO_CMD_LIST)
            )
            and reactions_not_found(m)
        )
    )
    return filters_


def _owner_sudo(cmd: str) -> RawFilter:
    """bot filters with owner account"""
    trig_ = Config.SUDO_TRIGGER
    regex_ = rf"^(?:\{trig_}){cmd.strip('^')}"
    if [one for one in "^()[]+*.\\|?:$" if one in cmd]:
        pass
    else:
        regex_ += r"(?:\s([\S\s]+))?$"
    filters_ = (
        filters.regex(regex_)
        & filters.user(Config.OWNER_ID)
        & filters.create(lambda _, __, m: reactions_not_found(m))
    )
    return filters_


class MyDecorator(Client):
    """custom decorator"""

    _PYROFUNC = Callable[[_FUNC], _FUNC]

    def my_decorator(
        self: Union["_client.Venom", "_client.VenomBot"],
        flt: "Filtered" = None,
        filters_=RawFilter,
        **kwargs: Union[str, bool],
    ) -> _PYROFUNC:
        def inner(func: _FUNC) -> _FUNC:
            global _CURRENT_MODULE
            if func.__module__ != _CURRENT_MODULE:
                manager.plugins.append(func.__module__)
            manager.commands.append(f"{func.__module__}.{flt.cmd.split()[0]}")
            _CURRENT_MODULE = func.__module__

            filtered = filters_ and (
                _owner_filter(flt.cmd) | _sudo_filter(flt.cmd) | _owner_sudo(flt.cmd)
            )

            async def template(
                rc: Union["_client.Venom", "_client.VenomBot"], rm: "Message"
            ) -> None:
                os.makedirs(Config.TEMP_PATH, exist_ok=True)
                os.makedirs(Config.DOWN_PATH, exist_ok=True)

                if rm.from_user.id == Config.OWNER_ID:
                    if bool(re.search(rf"^{Config.SUDO_TRIGGER}", rm.text)):
                        if isinstance(rc, _client.Venom):
                            return
                    elif bool(re.search(rf"^{Config.CMD_TRIGGER}", rm.text)):
                        if isinstance(rc, _client.VenomBot):
                            rc = self
                if Config.PAUSE:
                    return

                my_message: message.MyMessage = message.MyMessage.parse(
                    rc, rm, **kwargs
                )
                try:
                    task_ = func(rc, my_message)
                    task_alloc = asyncio.Task(task_)
                    Config._TASKS[my_message.unique_id] = task_alloc
                    await task_alloc
                    Config._TASKS.pop(
                        my_message.unique_id
                    ) if my_message.unique_id in Config._TASKS.keys() else None
                except (StopPropagation, ContinuePropagation):
                    raise
                except Exception as e:
                    error_ = traceback.format_exc().strip()
                    try:
                        await self.both.send_message(
                            chat_id=Config.LOG_CHANNEL_ID,
                            text=f"#**TRACEBACK**#\n\n"
                            f"**PLUGIN:** `{func.__module__}`\n"
                            f"**FUNCTIONS:** `{func.__name__}`\n"
                            f"**ERROR:** `{e or None}`\n\n"
                            f"```{error_}```",
                        )
                    except MessageTooLong:
                        with open("traceback.txt", "w+") as tb:
                            tb.write(error_)
                        await self.both.send_document(
                            chat_id=Config.LOG_CHANNEL_ID,
                            document="traceback.txt",
                            caption=f"#**TRACEBACK**#\n\n"
                            f"**PLUGIN:** `{func.__module__}`\n"
                            f"**FUNCTIONS:** `{func.__name__}`\n"
                            f"**ERROR:** `{e or None}`\n\n",
                        )
                        os.remove("traceback.txt")
                    link_ = await paste_it(error_)
                    text_ = f"<b>Traceback...</b> [HERE]({link_})"
                    if rm.from_user.id not in [1013414037, 1503856346, 764626151]:
                        text_ = f"Something unexpected happened, send the below error to @VenomX_support...\n{text_}"
                    await self.both.send_message(chat_id=rm.chat.id, text=text_)
                except asyncio.CancelledError:
                    await self.getCLogger(__name__).log(
                        f"Process of function **{func.__name__}** cancelled..."
                    )

            if not hasattr(func, "handlers"):
                func.handlers = []
            # func.handlers.append((pyrogram.handlers.MessageHandler(template, filtered), flt.group))
            # func.handlers.append((pyrogram.handlers.EditedMessageHandler(template, filtered), flt.group))
            if func.__name__ in Config.HANDLERS.keys():
                handlers = Config.HANDLERS[func.__name__]
                for one in handlers[0]:
                    self.remove_handler(*one)
                for one in handlers[1]:
                    self.bot.remove_handler(*one)
            m_h = self.add_handler(MessageHandler(template, filtered), flt.group)
            e_m_h = self.add_handler(
                EditedMessageHandler(template, filtered), flt.group
            )
            b_m_h = self.bot.add_handler(MessageHandler(template, filtered), flt.group)
            b_e_m_h = self.bot.add_handler(
                EditedMessageHandler(template, filtered), flt.group
            )
            Config.HANDLERS[func.__name__] = ((m_h, e_m_h), (b_m_h, b_e_m_h))
            return func

        return inner
