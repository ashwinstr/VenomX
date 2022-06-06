# send_message.py

import asyncio
from typing import Union, Optional

from pyrogram import Client as RClient
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.enums import ParseMode

from ... import types


class SendMessage(RClient):

    async def send_message(self,
                            chat_id: Union[int, str], 
                            text: str, 
                            del_in: int = -1,
                            dis_preview: bool = False,
                            parse_mode: ParseMode = ParseMode.DEFAULT,
                            reply_to_message_id: Optional[int] = None,
                            reply_markup: InlineKeyboardMarkup = None):

        " custom method for VenomX "

        msg = await super().send_message(chat_id=chat_id,
                                    text=text,
                                    disable_web_page_preview=dis_preview,
                                    parse_mode=parse_mode,
                                    reply_to_message_id=reply_to_message_id,
                                    reply_markup=reply_markup)
        
        if del_in >= 0:
            await asyncio.sleep(del_in)
            await msg.delete()
        
        return types.message.MyMessage.parse(msg)
