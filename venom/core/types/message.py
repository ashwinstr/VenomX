# message.py

import os
import re
from typing import List, Union

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.errors import (MessageAuthorRequired, MessageDeleteForbidden,
                             MessageIdInvalid, MessageTooLong)
from pyrogram.types import InlineKeyboardMarkup, Message
from pyromod import listen
from venom import Config

_CANCEL_PROCESS: List[int] = []


class MyMessage(Message):

    def __init__(self, message: Union[Message, 'MyMessage'], **kwargs) -> None:
        """ Modified Message """
        self.msg = message
        self.msg._flags = {}
        self.msg._filtered_input = ""
        for one in dir(message):
            if hasattr(self, one):
                continue
            if not one.startswith("__"):
                attr_ = getattr(message, one)
                try:
                    setattr(self, one, attr_)
                except:
                    pass
        # super().__init__(**kwargs)

    @classmethod
    def parse(cls, message, **kwargs):
        vars_ = vars(message)
        for one in ['_flags', '_filtered_input']:
            if one in vars_:
                del vars_[one]
        if vars_['reply_to_message']:
            vars_['reply_to_message'] = cls.parse(vars_['reply_to_message'], **kwargs)
        return cls(message, **kwargs)

    @property
    def replied(self) -> 'MyMessage':
        return self.reply_to_message

    @property
    def input_str(self) -> str:
        if not self.msg.text:
            return ""
        if " " in self.msg.text or "\n" in self.msg.text:
            text_ = self.msg.text
            split_ = text_.split(maxsplit=1)
            input_ = split_[-1]
            return input_
        return ''

    @property
    def flags(self) -> list:
        input_ = self.input_str
        if not input_:
            return []
        flags_ = []
        line_num = 0
        while True:
            first_line = input_.splitlines()[line_num]
            if first_line:
                break
            else:
                line_num += 1
        str_ = first_line.split()
        for one in str_:
            match = re.search(r"^(-[a-z]+)(\d.*)?$", one)
            if not hasattr(match, 'group'):
                break
            if match.group(2):
                flags_.append({
                    str(match.group(1)): int(match.group(2))
                })
            elif match.group(1):
                flags_.append(str(match.group(1)))
        return flags_

    @property
    def filtered_input(self) -> str:
        """ filter flags out and return string """
        input_ = self.input_str
        if not input_:
            return ""
        flags = self.flags
        for one in flags:
            if isinstance(one, dict):
                key_ = one.keys()[0]
                one = f"{key_}{one[key_]}"
            input_ = input_.lstrip(one).strip()
        return input_

    @property
    def process_is_cancelled(self) -> bool:
        """ check if process is cancelled """
        if self.msg.id in _CANCEL_PROCESS:
            _CANCEL_PROCESS.remove(self.msg.id)
            return True
        return False

    def cancel_process(self) -> None:
        """ cancel process """
        _CANCEL_PROCESS.append(self.msg.id)

    async def send_as_file(self,
                           text: str,
                           file_name: str = 'output.txt',
                           caption: str = '',
                           delete_message: bool = True,
                           reply_to: int = None) -> 'MyMessage':
        """ send text as file """
        file_ = os.path.join(Config.TEMP_PATH, file_name)
        with open(file_, "w+", encoding='utf-8') as fn:
            fn.write(str(text))
        if delete_message:
            try:
                await self.msg.delete()
            except MessageDeleteForbidden:
                pass
        if reply_to:
            reply_to_id = reply_to
        else:
            reply_to_id = self.msg.id if not self.msg.reply_to_message else self.msg.reply_to_message.id
        message = await self.msg._client.send_document(chat_id=self.msg.chat.id,
                                                       document=file_,
                                                       file_name=file_name,
                                                       caption=caption,
                                                       reply_to_message_id=reply_to_id)
        os.remove(file_)
        return self.parse(message)

    async def edit(self,
                   text: str,
                   dis_preview: bool = False,
                   del_in: int = -1,
                   parse_mode: ParseMode = ParseMode.DEFAULT,
                   reply_markup: InlineKeyboardMarkup = None,
                   sudo: bool = True,
                   **kwargs) -> 'MyMessage':
        """ edit or reply message """
        reply_to_id = self.replied.id if self.replied else self.id
        try:
            message = await self.msg._client.edit_message_text(
                chat_id=self.msg.chat.id,
                message_id=self.msg.id,
                text=text,
                del_in=del_in,
                parse_mode=parse_mode,
                dis_preview=dis_preview,
                reply_markup=reply_markup,
                **kwargs
            )
            return self.parse(message)
        except (MessageAuthorRequired, MessageIdInvalid):
            if sudo:
                reply_ = await self.msg._client.send_message(chat_id=self.msg.chat.id,
                                                             text=text,
                                                             del_in=del_in,
                                                             dis_preview=dis_preview,
                                                             parse_mode=parse_mode,
                                                             reply_markup=reply_markup,
                                                             reply_to_message_id=reply_to_id,
                                                             **kwargs)
                self.msg = reply_
                return self.parse(reply_)
            raise MessageAuthorRequired

    edit_text = try_to_edit = edit

    async def reply(self,
                    text: str,
                    dis_preview: bool = False,
                    del_in: int = -1,
                    parse_mode: ParseMode = ParseMode.DEFAULT,
                    reply_markup: InlineKeyboardMarkup = None,
                    quote: bool = True) -> 'MyMessage':
        """ reply message """

        reply_to_id = self.msg.reply_to_message.id if (quote and self.msg.reply_to_message) else None

        reply_ = await self.msg._client.send_message(chat_id=self.msg.chat.id,
                                                     text=text,
                                                     del_in=del_in,
                                                     dis_preview=dis_preview,
                                                     parse_mode=parse_mode,
                                                     reply_to_message_id=reply_to_id,
                                                     reply_markup=reply_markup)
        return reply_ if self.chat.type != ChatType.PRIVATE else self.parse(reply_)

    async def edit_or_send_as_file(self,
                                   text: str,
                                   file_name: str = "File.txt",
                                   caption: str = None,
                                   del_in: int = -1,
                                   parse_mode: ParseMode = ParseMode.DEFAULT,
                                   dis_preview: bool = False,
                                   **kwargs) -> 'MyMessage':
        """ edit or send as file """
        try:
            return await self.edit(
                text=text,
                del_in=del_in,
                parse_mode=parse_mode,
                dis_preview=dis_preview,
                **kwargs
            )
        except MessageTooLong:
            reply_to = self.replied.id if self.replied else self.id
            msg_ = await self.send_as_file(text=text,
                                           file_name=file_name,
                                           caption=caption,
                                           reply_to=reply_to)
            return msg_

    async def reply_or_send_as_file(self,
                                    text: str,
                                    file_name: str = "File.txt",
                                    caption: str = None,
                                    del_in: int = -1,
                                    parse_mode: ParseMode = ParseMode.DEFAULT,
                                    dis_preview: bool = False) -> 'MyMessage':
        """ reply or send as file """
        try:
            return await self.reply(text=text, del_in=del_in, parse_mode=parse_mode, dis_preview=dis_preview)
        except MessageTooLong:
            reply_to = self.replied.id if self.replied else self.id
            msg_ = await self.send_as_file(text=text,
                                           file_name=file_name,
                                           caption=caption,
                                           reply_to=reply_to)
            os.remove(file_name)
            return msg_

    async def delete(self) -> bool:
        """ message delete method """
        try:
            await self.msg.delete()
            return True
        except Exception as e:
            await self.msg._client.send_message(Config.LOG_CHANNEL_ID, f"Unable to delete...\nERROR: {e}")
            return False

    async def ask(self, text: str, timeout: int = 15, filters: filters.Filter = None) -> 'MyMessage':
        """ monkey patching to MyMessage using pyromod.ask """
        return await self.msg._client.ask(self.chat.id, text, timeout=timeout, filters=filters)

    async def wait(self, timeout: int = 15, filters: filters.Filter = None) -> 'MyMessage':
        """ monkey patching to MyMessage using pyromod's listen """
        return await self.msg._client.listen(self.chat.id, timeout=timeout, filters=filters)
