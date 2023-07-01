# message.py

import inspect
import os
import re
from typing import List, Union, Dict

from pyrogram import filters as flt, Client
from pyrogram.enums import ParseMode, ChatType
from pyrogram.errors import (MessageAuthorRequired, MessageDeleteForbidden,
                             MessageIdInvalid, MessageTooLong, MessageNotModified)
from pyrogram.types import InlineKeyboardMarkup, Message

import venom
from venom import Config, logging, SecureConfig
from .. import client as _client

_CANCEL_PROCESS: List[int] = []
_LOG = logging.getLogger(__name__)


class MyMessage(Message):

    def __init__(self,
                 client: Union['_client.Venom', '_client.VenomBot', 'Client'],
                 mvars: Dict[str, object],
                 **kwargs: Union[str, bool]) -> None:
        """ Modified Message """
        self._flags = []
        self._digital_flags = {}
        self._filtered_input = ""
        self._kwargs = kwargs
        # self._module = module
        self._client = client
        super().__init__(client=client, **mvars)

    @classmethod
    def parse(cls, client: Union['_client.Venom', '_client.VenomBot'], message: Message, **kwargs: Union[str, bool]):
        if not message:
            return
        vars_ = vars(message)
        for one in ['_client', '_digital_flags', '_flags', '_filtered_input', '_kwargs', '_module']:
            if one in vars_:
                del vars_[one]
        if vars_['reply_to_message']:
            vars_['reply_to_message'] = cls.parse(client, vars_['reply_to_message'], **kwargs)
        elif 'replied' in vars_.keys():
            vars_['replied'] = cls.parse(client, vars_['replied'], **kwargs)
        return cls(client, vars_, **kwargs)

    @property
    def client(self) -> Client:
        """ return client """
        return self._client

    @property
    def replied(self) -> Union['MyMessage', None]:
        if not hasattr(self, 'reply_to_message'):
            return None
        replied_msg = self.reply_to_message
        return replied_msg

    @property
    def input_str(self) -> str:
        if not self.text:
            return ""
        if " " in self.text or "\n" in self.text:
            text_ = self.text
            split_ = text_.split(maxsplit=1)
            input_ = split_[-1]
            return input_
        return ''

    @property
    def flags(self) -> list:
        """ flags as options """
        input_ = self.input_str
        if not input_:
            return []
        string_ = input_.splitlines()[0]
        pattern_ = r"-[a-z]+\d*"
        try:
            flags_ = re.findall(pattern_, string_)
        except Exception as e:
            _LOG.error("Error: %s", e)
            return []
        return flags_

    @property
    def digital_flags(self) -> dict:
        """ flags with digit as suffix """
        input_ = self.input_str
        if not input_:
            return {}
        flag_string_ = input_.splitlines()[0]
        pattern_ = r"-[a-z]+\d+"
        try:
            flags_ = re.findall(pattern_, flag_string_)
        except Exception as e:
            _LOG.error("Error: %s", e)
            return {}
        dict_ = {}
        for one in flags_:
            search_ = re.search(r"(-[a-z]+)(\d+)", one)
            dict_[search_.group(1)] = int(search_.group(2))
        return dict_

    @property
    def filtered_input(self) -> str:
        """ filter flags out and return string """
        input_ = self.input_str
        if not input_:
            return ""
        flags = self.flags
        old_first_line = input_.splitlines()[0]
        new_first_line = old_first_line
        for one in flags:
            new_first_line = new_first_line.replace(one, "")
        input_ = input_.replace(old_first_line, new_first_line.strip())
        return input_.strip()

    @property
    def process_is_cancelled(self) -> bool:
        """ check if process is cancelled """
        if self.id in _CANCEL_PROCESS:
            _CANCEL_PROCESS.remove(self.id)
            return True
        return False

    def cancel_process(self) -> None:
        """ cancel process """
        _CANCEL_PROCESS.append(self.id)

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
                await self.delete()
            except MessageDeleteForbidden:
                pass
        if reply_to:
            reply_to_id = reply_to
        else:
            reply_to_id = self.id if not self.reply_to_message else self.reply_to_message.id
        message = await self._client.send_document(chat_id=self.chat.id,
                                                   document=file_,
                                                   file_name=file_name,
                                                   caption=caption,
                                                   reply_to_message_id=reply_to_id)
        module = inspect.currentframe().f_back.f_globals['__name__']
        os.remove(file_)
        return self.parse(self._client, message)

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
            message = await self._client.edit_message_text(
                chat_id=self.chat.id,
                message_id=self.id,
                text=text,
                del_in=del_in,
                parse_mode=parse_mode,
                dis_preview=dis_preview,
                reply_markup=reply_markup,
                **kwargs
            )
            return message
        except MessageNotModified:
            return self
        except (MessageAuthorRequired, MessageIdInvalid) as msg_err:
            if sudo:
                reply_ = await self._client.send_message(chat_id=self.chat.id,
                                                         text=text,
                                                         del_in=del_in,
                                                         dis_preview=dis_preview,
                                                         parse_mode=parse_mode,
                                                         reply_markup=reply_markup,
                                                         reply_to_message_id=reply_to_id,
                                                         **kwargs)
                if isinstance(reply_, MyMessage):
                    self.id = reply_.id
                return reply_
            raise msg_err

    edit_text = try_to_edit = edit

    async def err(self, text: str):
        """ Method for showing errors """
        format_ = f"<b>Error</b>:\n{text}"
        try:
            return await self.edit(text)
        except Exception as e:
            venom.test_print(e)

    async def reply(self,
                    text: str,
                    dis_preview: bool = False,
                    del_in: int = -1,
                    parse_mode: ParseMode = ParseMode.DEFAULT,
                    reply_markup: InlineKeyboardMarkup = None,
                    quote: bool = True,
                    **kwargs) -> 'MyMessage':
        """ reply message """

        reply_to_id = self.replied.id if (quote and self.replied) else None

        reply_ = await self._client.send_message(chat_id=self.chat.id,
                                                 text=text,
                                                 del_in=del_in,
                                                 dis_preview=dis_preview,
                                                 parse_mode=parse_mode,
                                                 reply_to_message_id=reply_to_id,
                                                 reply_markup=reply_markup,
                                                 **kwargs)
        return reply_

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

    async def delete(self, revoke: bool = True) -> bool:
        """ message delete method """
        try:
            await super().delete()
            return True
        except MessageAuthorRequired:
            return False

    async def ask(self, text: str, timeout: int = 15, filters: flt.Filter = None) -> 'MyMessage':
        """ monkey patching to MyMessage using pyromod.ask """
        return await self._client.ask(chat_id=self.chat.id, text=text, timeout=timeout, filters=filters)

    async def wait(self, timeout: int = 15, filters: flt.Filter = None) -> 'MyMessage':
        """ monkey patching to MyMessage using pyromod.listen """
        return await self._client.listen(self.chat.id, timeout=timeout, filters=filters)

    async def copy_content(self, chat_id: Union[int, str] = "me") -> 'MyMessage':
        """ copy content in restricted chat """
        if self.chat.type == ChatType.PRIVATE:
            return await self.edit("`This method is for groups only...`", del_in=5)
        msg_link = self.link
        pattern_ = re.compile(r"https://t.me/(\w+)/(\d+)")
        match_ = re.search(pattern_, msg_link)
        from_chat = match_.group(1) or None
        msg_id = match_.group(2) or None
        if from_chat.isdigit():
            from_chat = int("-100" + from_chat)
        content_ = (await self._client.get_messages(from_chat, [int(msg_id)]))[0]
        un_parsed_ = await content_.copy(chat_id=chat_id)
        return self.parse(self._client, un_parsed_)
