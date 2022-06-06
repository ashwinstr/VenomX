# edit_message_text.py

import asyncio
from typing import Union

from pyrogram import Client as RClient
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.enums import ParseMode

from ... import types

class EditMessageText(RClient):

    async def edit_message_text(self,
                                chat_id: Union[str, int],
                                message_id: int,
                                text: str,
                                del_in: int = -1,
                                dis_preview: bool = False,
                                parse_mode: ParseMode = ParseMode.DEFAULT,
                                reply_markup: InlineKeyboardMarkup = None):

        " custom edit_message_text method for VenomX "

        msg = await super().edit_message_text(chat_id=chat_id,
                                                message_id=message_id,
                                                text=text,
                                                disable_web_page_preview=dis_preview,
                                                parse_mode=parse_mode,
                                                reply_markup=reply_markup)

        if del_in >= 0:
            await asyncio.sleep(del_in)
            await msg.delete()
        
        return types.message.MyMessage.parse(msg)