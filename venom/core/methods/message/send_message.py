# send_message.py

import asyncio
from typing import Optional, List, Union

from pyrogram import Client as RClient
from pyrogram.enums import ParseMode
from pyrogram.types import MessageEntity, ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove

from ... import types


class SendMessage(RClient):

    async def send_message(self,
                            chat_id: Union[str, int],
                            text: str,
                            del_in: int = -1,
                            dis_preview: Optional[bool] = None,
                            entities: List[MessageEntity] = None,
                            parse_mode: Union[str, ParseMode] = ParseMode.DEFAULT,
                            protect_content: Optional[bool] = False,
                            reply_to_message_id: Optional[int] = None,
                            reply_markup: Union[
                                ReplyKeyboardRemove,
                                ReplyKeyboardMarkup,
                                InlineKeyboardMarkup
                            ] = None) -> 'types.message.MyMessage':

        " custom method for VenomX "

        disable_web_page_preview = True if dis_preview else None

        msg = await super().send_message(chat_id=chat_id,
                                            text=text,
                                            disable_web_page_preview=disable_web_page_preview,
                                            entities=entities,
                                            parse_mode=parse_mode,
                                            protect_content=protect_content,
                                            reply_to_message_id=reply_to_message_id,
                                            reply_markup=reply_markup)
        
        if del_in >= 0:
            await asyncio.sleep(del_in)
            await msg.delete()
        
        return types.message.MyMessage.parse(msg)
