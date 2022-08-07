# filters.py

import os

from pyrogram import filters

OWNER = os.environ['OWNER_ID']


class MyFilters:

    async def Edited(_, __, message):
        return hasattr(message, 'edit_date') and message.edit_date
    edited = filters.create(Edited)

    async def ReplyToMe(_, __, message):
        if message.reply_to_message.from_user.id == int(OWNER):
            return True
    reply_me = filters.create(ReplyToMe)