# alive.py

import asyncio
import re

from pyrogram import __version__ as ver, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultAnimation,
    InlineQueryResultVideo,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from pyrogram.enums import MessageMediaType

from venom import venom, Config, Collection, MyMessage, python_ver
from venom.helpers import plugin_name, post_tg_media, VenomDecorators


HELP = Config.HELP[plugin_name(__name__)] = {'type': 'fun', 'commands': []}
ALIVE_PIC = Collection.ALIVE_MEDIA
DOT_ = Config.BULLET_DOT

async def _init() -> None:
    " loading alive pics "
    found = await ALIVE_PIC.find_one({'_id': 'ALIVE_PIC'})
    if found:
        Config.ALIVE_PIC = found['pic_url']
    else:
        await ALIVE_PIC.insert_one({'_id': 'ALIVE_PIC', 'pic_url': Config.DEFAULT_ALIVE_PIC})
        Config.ALIVE_PIC = Config.DEFAULT_ALIVE_PIC


#########################################################################################################################################################


HELP['commands'].append(
    {
        'command': 'setalive',
        'flags': {
            '-c': 'check url',
            '-r': 'reset url'
        },
        'about': "set bot's alive media",
        'sudo': True
    }
)

@venom.trigger('setalive')
async def set_alive(_, message: MyMessage):
    " set bot's alive media "
    if '-c' in message.flags:
        out_ = "Your <b>alive pic</b> link is [<b>HERE</b>]({})"
        return await message.edit(out_.format(Config.ALIVE_PIC), dis_preview=True)
    elif '-r' in message.flags:
        if Config.ALIVE_PIC == Config.DEFAULT_ALIVE_PIC:
            return await message.edit("`Your alive pic is already default.`")
        Config.ALIVE_PIC = Config.DEFAULT_ALIVE_PIC
        await ALIVE_PIC.update_one(
            {'_id': 'ALIVE_PIC'}, {'$set': {'pic_url': Config.ALIVE_PIC}}, upsert=True
        )
        Config.ALIVE_PIC_TYPE = MessageMediaType.PHOTO
        return await message.edit("`Alive media reset to default.`")
    reply_ = message.replied
    if not reply_:
        link_ = message.input_str
        if not link_:
            return await message.edit("`Reply to media or input telegraph link to set as alive media...`")
    else:
        link_ = await post_tg_media(message)
    check_link = re.search(r"^http[s]?\:\/\/telegra\.ph/file/\w.*\.((mp4)|(mkv)|(gif)|(jpg)|(jpeg)|(png))", link_)
    if not bool(check_link):
        return await message.edit("`Invalid link.`")
    Config.ALIVE_PIC = link_
    match = check_link.group(1)
    Config.ALIVE_PIC_TYPE = MessageMediaType.PHOTO if match in ("jpg", "jpeg", "png") else MessageMediaType.ANIMATION if match == "gif" else MessageMediaType.VIDEO
    await ALIVE_PIC.update_one(
        {'_id': 'ALIVE_PIC'}, {'$set': {'pic_url': Config.ALIVE_PIC}}, upsert=True
    )
    await message.edit("Your <b>alive media</b> is set to [<b>THIS</b>]({})".format(Config.ALIVE_PIC), dis_preview=True)


#########################################################################################################################################################################


HELP['commands'].append(
    {
        'command': 'alive',
        'flags': None,
        'about': 'check bot info in fancy way',
        'sudo': True
    }
)

@venom.trigger('alive')
async def bot_alive(_, message: MyMessage):
    " check bot info in fancy way "
    bot_ = (await venom.bot.get_me()).username
    reply_to_id = message.replied.id if message.replied else None
    results = await venom.get_inline_bot_results(
        bot=bot_,
        query="alive"
    )
    await asyncio.gather(
        venom.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id,
            reply_to_message_id=reply_to_id
        ),
        message.delete()
    )


#########################################################################################################################################################################


class AliveInfo:

    @staticmethod
    def alive_info(user_) -> str:
        " alive inline caption "
        info_ = f"""
<b>[VenomX](https://github.com/ashwinstr/VenomX)</b> is functioning.

{DOT_} <b>User {':':>12}</b> `{user_}`
{DOT_} <b>Python {':':>7}</b> `{python_ver}`
{DOT_} <b>Pyro {':':>12}</b> `{ver}`
{DOT_} <b>Owner {':':>8}</b> [Kakashi](https://t.me/Kakashi_HTK)

<b>Support:</b> [VenomX Support](https://t.me/AntiVenom_X)
"""
        return info_

    @staticmethod
    def alive_buttons() -> InlineKeyboardMarkup:
        " alive inline buttons "
        btn_ = [
            [
                InlineKeyboardButton(text="REPO", url=Config.UPSTREAM_REPO),
                InlineKeyboardButton(text="INFO", callback_data="INFO")
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=btn_)


########################################################################################################################################################################


@venom.bot.on_inline_query(filters.regex("^alive$"))
@VenomDecorators.inline_checker(owner=True)
async def alive_media_inline(_, i_q: InlineQuery):
    " alive media inline query "
    iq = i_q.query
    results = []
    if iq == "alive":
        user_ = (await venom.get_me()).mention
        btns_ = AliveInfo.alive_buttons()
        cap_ = AliveInfo.alive_info(user_)
        if Config.ALIVE_PIC_TYPE == MessageMediaType.PHOTO:
            results.append(
                InlineQueryResultPhoto(
                    title="Alive media.",
                    photo_url=Config.ALIVE_PIC,
                    caption=cap_,
                    reply_markup=btns_,
                )
            )
        elif Config.ALIVE_PIC_TYPE == MessageMediaType.ANIMATION:
            results.append(
                InlineQueryResultAnimation(
                    title="Alive media.",
                    animation_url=Config.ALIVE_PIC,
                    caption=cap_,
                    reply_markup=btns_,
                )
            )
        elif Config.ALIVE_PIC_TYPE == MessageMediaType.VIDEO:
            results.append(
                InlineQueryResultVideo(
                    title="Alive media.",
                    video_url=Config.ALIVE_PIC,
                    caption=cap_,
                    reply_markup=btns_,
                )
            )
        else:
            HELP_MENU = InlineQueryResultArticle(
                title="VenomX error.",
                input_message_content=InputTextMessageContent(
                    message_text="Content not found."
                )
            )
            results.append(HELP_MENU)
    if len(results) != 0:
        await i_q.answer(results=results, cache_time=1)


#################################################################################################################################################################


@venom.bot.on_callback_query(filters.regex("^INFO$"))
@VenomDecorators.callback_checker()
async def bot_info(_, cq: CallbackQuery):
    info_ = f"""
### Information about VenomX ###

{DOT_} Owner: Kakashi
{DOT_} Based on:
    USERGE/USERGE-X
    (for understanding core parts)
{DOT_} Release date: NO ETA
"""
    await cq.answer(info_, show_alert=True)