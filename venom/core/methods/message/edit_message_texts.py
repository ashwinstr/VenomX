# edit_message_texts.py

import asyncio
from typing import Union

from pyrogram import Client as RClient
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, MessageEntity

from ... import types


class EditMessageText(RClient):

    async def edit_message_text(self,
                                chat_id: Union[str, int],
                                message_id: int,
                                text: str,
                                del_in: int = -1,
                                dis_preview: bool = False,
                                entities: MessageEntity = None,
                                parse_mode: ParseMode = ParseMode.DEFAULT,
                                reply_markup: InlineKeyboardMarkup = None) -> 'types.message.MyMessage':
        """ custom edit_message_text method for VenomX """

        disable_web_page_preview = True if dis_preview else False

        msg = await super().edit_message_text(chat_id=chat_id,
                                              message_id=message_id,
                                              text=text,
                                              disable_web_page_preview=disable_web_page_preview,
                                              entities=entities,
                                              parse_mode=parse_mode,
                                              reply_markup=reply_markup)

        if del_in >= 0:
            await asyncio.sleep(del_in)
            await msg.delete()

        return types.message.MyMessage.parse(msg)
