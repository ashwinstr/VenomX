# filters.py

import os

from pyrogram import filters
from pyrogram.types import Message

from venom import Config

OWNER = os.environ['OWNER_ID']


async def _edited(_, __, message: Message) -> bool:
    """ custom edited filter for pyromod """
    return hasattr(message, 'edit_date') and message.edit_date


async def _reply_to_me(_, __, message: Message) -> bool:
    """ replied to the owner """
    if message.reply_to_message\
        and message.reply_to_message.from_user\
            and message.reply_to_message.from_user.id == int(OWNER):
        return True
    return False


async def _mentioned_me(_, __, message: Message) -> bool:
    """ mentioned the owner """
    text_ = message.text.html
    if Config.OWNER_ID in text_:
        return True
    return False


class MyFilters:

    edited = filters.create(_edited)
    reply_me = filters.create(_reply_to_me)
    mentioned_me = filters.create(_mentioned_me)