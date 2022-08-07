# testing plugin test.py

import pyromod.filters

from pyrogram import filters as flt, Client
from pyrogram.handlers import EditedMessageHandler

from venom import venom, MyMessage


""" async def asking(cl: Client, msg: MyMessage):
    asked_ = await cl.ask(msg.chat.id, "WHAT!?")
    return asked_

@venom.trigger('test')
async def test_ing(_, message: MyMessage):
    " test "
    venom.add_handler(
        EditedMessageHandler(
            asking,
            filters.create(
                lambda _, __, m:
                m.edit_date is not None
            )
        )
    )
    asked = await asking(venom, message)
    await message.edit_or_send_as_file(asked.text) """

@venom.trigger('test')
async def testing_(_, message: MyMessage):
    " testing "
    test_ = await venom.ask(message.chat.id, "test", filters=flt.edit)
    await message.edit(test_.text)