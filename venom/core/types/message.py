# message.py

import re
import os
import json

from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageAuthorRequired, MessageTooLong

from pyromod import listen

from venom import Config


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

    @property
    def replied(self) -> 'MyMessage':
        return self.msg.reply_to_message

    @property
    def user(self):
        return self.msg.from_user

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

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    async def send_as_file(self,
                            text: str,
                            file_name: str = 'output.txt',
                            caption: str = '',
                            delete_message: bool = True,
                            reply_to_message_id: int = None) -> 'MyMessage':
        " send text as file "
        file_ = os.path.join(Config.TEMP_PATH, file_name)
        with open(file_, "w+", encoding='utf-8') as fn:
            fn.write(text)
        if delete_message:
            await self.msg.delete()
        if reply_to_message_id:
            reply_to_id = reply_to_message_id
        else:
            reply_to_id = self.msg.id if not self.msg.reply_to_message else self.msg.reply_to_message.id
        return await self.msg._client.send_document(chat_id=self.msg.chat.id,
                                                    document=file_,
                                                    file_name=file_name,
                                                    caption=caption,
                                                    reply_to_message_id=reply_to_id)


    async def edit(self,
                    text: str,
                    sudo: bool = True,
                    parse_mode: ParseMode = ParseMode.DEFAULT,
                    dis_preview: bool = False) -> 'MyMessage':
        " edit or reply message "
        reply_to_id = self.replied.id if self.replied else self.id
        try:
            return await self.msg._client.edit_message_text(
                chat_id=self.msg.chat.id,
                message_id=self.msg.id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=dis_preview
            )
        except MessageAuthorRequired:
            if sudo:
                reply_ = await self.msg._client.send_message(chat_id=self.msg.chat.id,
                                                                text=text,
                                                                disable_web_page_preview=dis_preview,
                                                                parse_mode=parse_mode,
                                                                reply_to_message_id=reply_to_id)
                self.msg = reply_
                return reply_
            raise MessageAuthorRequired
    
    edit_text = try_to_edit = edit

    async def edit_or_send_as_file(self,
                                    text: str,
                                    file_name: str,
                                    caption: str,
                                    parse_mode: ParseMode = ParseMode.DEFAULT,
                                    dis_preview: bool = False) -> 'MyMessage':
        " edit or send as file "
        try:
            return await self.edit(text=text, parse_mode=parse_mode, dis_preview=dis_preview)
        except MessageTooLong:
            reply_to = self.replied.id if self.replied else self.id
            return await self.send_as_file(text=text,
                                            file_name=file_name,
                                            caption=caption,
                                            reply_to_message_id=reply_to)
    
    async def ask(self, text: str, timeout: int = 15) -> 'MyMessage':
        " monkey patching to MyMessage using pyromod "
        return await self._client.ask(self.chat.id, text, timeout=timeout)