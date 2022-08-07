# message.py

import re
import os
from typing import List

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageAuthorRequired, MessageTooLong, MessageIdInvalid

from pyromod import listen

from venom import Config

_CANCEL_PROCESS: List[int] = []


class MyMessage(Message):

    def __init__(self, message: Message) -> None:
        " testing "
        self.msg = message
        self.msg._flags = {}
        self.msg._filtered_input = ""
        for one in dir(message):
            if hasattr(self, one):
                continue
            if not one.startswith("__"):
                attr_ = getattr(message, one)
                setattr(self, one, attr_)
#        self.__dict__ = message.__dict__.copy()
#        super().__init__()

    @classmethod
    def parse(cls, message):
        return cls(message)

    @property
    def replied(self) -> 'MyMessage':
        return self.msg.reply_to_message

    @property
    def input_str(self) -> str:
        if " " in self.msg.text or "\n" in self.msg.text:
            text_ = self.msg.text
            split_ = text_.split(maxsplit=1)
            input_ = split_[-1]
            return input_
        return None

    @property
    def flags(self):
        input_ = self.input_str
        if not input_:
            return []
        flags_ = []
        first_line = input_.splitlines()
        for string in first_line:
            str_ = string.split()
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
    def filtered_input(self):
        input_ = self.input_str
        filtered = ""
        if not input_:
            return filtered
        for lines in input_.splitlines():
            new_line = ""
            for word in lines.split(" "):
                if word.startswith("-"):
                    continue
                else:
                    new_line += f"{word} "
            filtered += f"\n{new_line}"
        return filtered.strip()

    @property
    def process_is_cancelled(self) -> bool:
        " check if process is cancelled "
        if self.msg.id in _CANCEL_PROCESS:
            _CANCEL_PROCESS.remove(self.msg.id)
            return True
        return False

    def cancel_process(self) -> None:
        " cancel process "
        _CANCEL_PROCESS.append(self.msg.id)

    async def send_as_file(self,
                            text: str,
                            file_name: str = 'output.txt',
                            caption: str = '',
                            delete_message: bool = True,
                            reply_to: int = None) -> 'MyMessage':
        " send text as file "
        file_ = os.path.join(Config.TEMP_PATH, file_name)
        with open(file_, "w+", encoding='utf-8') as fn:
            fn.write(str(text))
        if delete_message:
            await self.msg.delete()
        if reply_to:
            reply_to_id = reply_to
        else:
            reply_to_id = self.msg.id if not self.msg.reply_to_message else self.msg.reply_to_message.id
        return await self.msg._client.send_document(chat_id=self.msg.chat.id,
                                                    document=file_,
                                                    file_name=file_name,
                                                    caption=caption,
                                                    reply_to_message_id=reply_to_id)


    async def edit(self,
                    text: str,
                    dis_preview: bool = False,
                    del_in: int = -1,
                    parse_mode: ParseMode = ParseMode.DEFAULT,
                    reply_markup: InlineKeyboardMarkup = None,
                    sudo: bool = True) -> 'MyMessage':
        " edit or reply message "
        reply_to_id = self.replied.id if self.replied else self.id
        try:
            return await self.msg._client.edit_message_text(
                chat_id=self.msg.chat.id,
                message_id=self.msg.id,
                text=text,
                del_in=del_in,
                parse_mode=parse_mode,
                dis_preview=dis_preview,
                reply_markup=reply_markup
            )
        except (MessageAuthorRequired, MessageIdInvalid):
            if sudo:
                reply_ = await self.msg._client.send_message(chat_id=self.msg.chat.id,
                                                                text=text,
                                                                del_in=del_in,
                                                                dis_preview=dis_preview,
                                                                parse_mode=parse_mode,
                                                                reply_markup=reply_markup,
                                                                reply_to_message_id=reply_to_id)
                self.msg = reply_
                return reply_
            raise MessageAuthorRequired
    
    edit_text = try_to_edit = edit

    async def reply(self,
                    text: str,
                    dis_preview: bool = False,
                    del_in: int = -1,
                    parse_mode: ParseMode = ParseMode.DEFAULT,
                    reply_markup: InlineKeyboardMarkup = None,
                    quote: bool = True) -> 'MyMessage':
        " reply message "

        reply_to_id = self.msg.reply_to_message.id if quote and self.msg.reply_to_message else None

        return await self.msg._client.send_message(chat_id=self.msg.chat.id,
                                                    text=text,
                                                    del_in=del_in,
                                                    dis_preview=dis_preview,
                                                    parse_mode=parse_mode,
                                                    reply_to_message_id=reply_to_id,
                                                    reply_markup=reply_markup)

    async def edit_or_send_as_file(self,
                                    text: str,
                                    file_name: str = "File.txt",
                                    caption: str = None,
                                    del_in: int = -1,
                                    parse_mode: ParseMode = ParseMode.DEFAULT,
                                    dis_preview: bool = False) -> 'MyMessage':
        " edit or send as file "
        try:
            return await self.edit(text=text, del_in=del_in, parse_mode=parse_mode, dis_preview=dis_preview)
        except MessageTooLong:
            reply_to = self.replied.id if self.replied else self.id
            return await self.send_as_file(text=text,
                                            file_name=file_name,
                                            caption=caption,
                                            reply_to=reply_to)
    
    async def ask(self, text: str, timeout: int = 15, filters: filters.Filter = None) -> 'MyMessage':
        " monkey patching to MyMessage using pyromod "
        return await self.msg._client.ask(self.chat.id, text, timeout=timeout, filters=filters)