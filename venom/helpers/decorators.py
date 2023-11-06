# decorators.py

import traceback
import asyncio

from pyrogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)
from pyrogram.errors import FloodWait

from venom import Config


class VenomDecorators:

    @staticmethod
    def callback_checker(owner: bool = False, sudo: bool = True):
        def function(func):
            async def wrapper(venom, c_q: CallbackQuery):
                """ callback query owner and tb checker """
                user_id = c_q.from_user.id
                if owner and user_id != Config.OWNER_ID:
                    "owner check"
                    if not sudo and (user_id in Config.SUDO_USERS or user_id in Config.TRUSTED_SUDO_USERS):
                        return await c_q.answer("Sudo is disabled for this function.", show_alert=True)
                    if not Config.SUDO \
                            or (user_id not in Config.SUDO_USERS
                                and user_id not in Config.TRUSTED_SUDO_USERS):
                        " if not owner "
                        return await c_q.answer(
                            f"Only my owner can access this...!\nPlease deploy your own VenomX bot, thank you.",
                            show_alert=True)
                try:
                    await func(venom, c_q)
                except FloodWait as e:
                    await asyncio.sleep(e.value + 3)
                except Exception as e:
                    await venom.send_message(Config.LOG_CHANNEL_ID,
                                             text=f"### **CALLBACK TRACEBACK** ###\n\n"
                                                  f"**PLUGIN:** `{func.__module__}`\n"
                                                  f"**FUNCTION:** `{func.__name__}`\n"
                                                  f"**ERROR:** `{e or None}`\n\n"
                                                  f"```python\n{traceback.format_exc().strip()}```")

            return wrapper

        return function

    # def no_group(func):
    #     async def wrapper(venom, message: 'MyMessage'):
    #         if message.chat.type == ChatType.SUPERGROUP:
    #             print(message.id)
    #             return await message.edit("`Invalid chat type: SUPERGROUP!`")
    #         await func(venom, message)
    #     return wrapper

    @staticmethod
    def inline_checker(owner: bool = False):
        def function(func):
            async def wrapper(venom, iq: InlineQuery):
                """ inline query owner and tb checker """
                user_id = iq.from_user.id
                if owner and user_id != Config.OWNER_ID:
                    " owner check "
                    if (
                        user_id not in Config.SUDO_USERS
                        and user_id not in Config.TRUSTED_SUDO_USERS
                    ):
                        " if not owner "
                        results = [InlineQueryResultArticle(
                            title="VenomX",
                            input_message_content=InputTextMessageContent(
                                "Only the <b>owner and sudo users</b> can use this bot. Please deploy your own "
                                "<b>VenomX</b>."
                            ),
                        )]
                        return await iq.answer(results=results, cache_time=5)
                try:
                    await func(venom, iq)
                except FloodWait as e:
                    await asyncio.sleep(e.value + 3)
                except Exception as e:
                    await venom.send_message(Config.LOG_CHANNEL_ID,
                                             text=f"### **INLINE_QUERY TRACEBACK** ###\n\n"
                                                  f"**PLUGIN:** `{func.__module__}`\n"
                                                  f"**FUNCTION:** `{func.__name__}`\n"
                                                  f"**ERROR:** `{e or None}`\n\n"
                                                  f"```python\n{traceback.format_exc().strip()}```")

            return wrapper

        return function
