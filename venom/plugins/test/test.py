# testing plugin test.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from venom import venom, MyMessage
from venom.helpers import VenomDecorators


@venom.trigger('test')
async def test_ing(_, message: MyMessage):
    " testing plugin "
    btn_ = [
        [
            InlineKeyboardButton(text="TEST", callback_data="TEst")
        ]
    ]
    x = InlineKeyboardMarkup(btn_)
    await venom.bot.send_message(message.chat.id, "TESTING", reply_markup=x)


@venom.bot.on_callback_query(filters.regex("^TEst$"))
@VenomDecorators.callback_checker(owner=True)
async def tes_ting(_, c_q: CallbackQuery):
    " testing callback "
    await c_q.answer("Working!", show_alert=True)