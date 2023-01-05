# secret.py

import asyncio

from pyrogram import filters
from pyrogram.types import (
    InlineQuery, 
    InlineQueryResultArticle, 
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from pyrogram.errors import MessageNotModified, PeerIdInvalid

from venom import venom, Collection, Config, MyMessage
from venom.helpers import VenomDecorators, plugin_name


HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'fun', 'commands': []}

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'dsecrets',
        'flags': None,
        'usage': 'destroy all secrets',
        'syntax': '{tr}dsecret',
        'sudo': False
    }
)


@venom.trigger('dsecrets')
async def destroy_secrets(_, message: MyMessage):
    """ destroy all secrets """
    await message.edit("`Destroying secrets...`")
    await Collection.SECRET.drop()
    await message.edit("`All secrets destroyed !!!`", del_in=5)

########################################################################################################################


@venom.bot.on_inline_query(filters.regex(r"^(\@\w+) \<s\>(.*)\<\/s\>$"))
@VenomDecorators.inline_checker(owner=True)
async def secret_whisper(_, i_q: InlineQuery):
    """ inline query for secret message """
    results = []
    for_ = i_q.matches[0].group(1)
    try:
        user_ = await venom.get_users(for_)
    except PeerIdInvalid:
        return
    msg_ = i_q.matches[0].group(2)
    id_ = venom.rnd_id()
    results.append(
        InlineQueryResultArticle(
            title="Secret whisper.",
            input_message_content=InputTextMessageContent(
                message_text=f"You have sent a secret message.\nfor <b>{user_.mention}</b>..."
            ),
            reply_markup=activate_button(id_)
        )
    )
    if len(results) != 0:
        await asyncio.gather(
            i_q.answer(results=results, cache_time=1),
            Collection.SECRET.insert_one(
                {
                    '_id': id_,
                    'msg': msg_,
                    'from': i_q.from_user.id,
                    'for': user_.id
                }
            )
        )


@venom.bot.on_callback_query(filters.regex(r"^(deactivate|activate)_(\d+)"))
@VenomDecorators.callback_checker(owner=True)
async def activate_secret_callback(_, c_q: CallbackQuery):
    """ callback query for secret message """
    query_ = c_q.matches[0].group(1)
    id_ = c_q.matches[0].group(2)
    if query_ == "activate":
        reply_markup = secret_button(id_)
    else:
        reply_markup = activate_button(id_)
    await c_q.edit_message_reply_markup(reply_markup=reply_markup)


@venom.bot.on_callback_query(filters.regex(r"^secret_(\d+)"))
@VenomDecorators.callback_checker()
async def secret_callback(_, c_q: CallbackQuery):
    """ callback query for secret message """
    id_ = c_q.matches[0].group(1)
    found_ = await Collection.SECRET.find_one({'_id': int(id_)})
    if found_:
        for_ = found_['for']
        from_ = found_['from']
        msg_ = found_['msg']
        if c_q.from_user.id == from_:
            pass
        elif c_q.from_user.id == for_:
            try:
                await c_q.edit_message_text(text=f"Secret whisper...\n<b>Seen!</b>", reply_markup=secret_button(id_))
            except MessageNotModified:
                pass
        else:
            msg_ = "This secret is not for you !!!"
        await c_q.answer(msg_, show_alert=True)
    else:
        await c_q.answer(text="Message destroyed!", show_alert=True)


def activate_button(rnd_id: int) -> InlineKeyboardMarkup:
    """ return activate button """
    btns_ = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Activate?", callback_data=f"activate_{rnd_id}")
            ]
        ]
    )
    return btns_


def secret_button(rnd_id: int) -> InlineKeyboardMarkup:
    """ return secret button """
    btn_ = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Check", callback_data=f"secret_{rnd_id}"),
                InlineKeyboardButton(text="De-activate", callback_data=f"deactivate_{rnd_id}")
            ]
        ]
    )
    return btn_
