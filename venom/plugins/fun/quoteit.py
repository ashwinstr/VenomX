# quoteit.py

import asyncio
import json
import os

from pyrogram import filters
from venom import Config, MyMessage, venom


@venom.trigger("qit")
async def quote_message(_, message: MyMessage):
    " quote support in ub "
    from_user_ = message.from_user.id
    flags_ = message.flags
    try:
        await venom.get_chat_member(-1001331162912, from_user_)
    except BaseException as e:
        if from_user_ not in Config.TRUSTED_SUDO_USERS:
            return await message.edit("First join **@UX_xplugin_support** and get approved by Kakashi.")
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to message...`", del_in=5)
    name_ = reply_.from_user.first_name
    pfp_ = reply_.from_user.photo.big_file_id if reply_.from_user.photo else None
    text_ = reply_.text if "-f" not in flags_ else message.filtered_input
    fake_ = True if "-f" in flags_ else False
    if not text_:
        return await message.edit("`Text not found...`", del_in=5)
    await message.edit("`Making quote...`")
    if "-r" in flags_:
        reply_msg = await venom.get_messages(message.chat.id, reply_.id)
        reply_name = reply_msg.reply_to_message.from_user.first_name
        reply_text = (reply_msg.reply_to_message.text).splitlines()[0]
    else:
        reply_name = None
        reply_text = None
    bot_ = "QuoteIT_thebot"
    form_ = {
        "cmd": "QUOTE_IT",
        "name": name_,
        "text": text_,
        "reply_name": reply_name,
        "reply_text": reply_text,
        "fake": fake_,
    }
    json_ = json.dumps(form_, indent=4)
    if pfp_:
        down_ = await venom.download_media(pfp_)
        req_ = await venom.send_photo(bot_, down_, caption=json_)
        req_ = MyMessage.parse(req_)
        os.remove(down_)
    else:
        req_ = await venom.send_message(bot_, json_)
    try:
        resp_ = await req_.wait(timeout=20, filters=(filters.bot))
    except TimeoutError:
        return await message.edit("`Bot didn't respond...`", del_in=5)
    resp = resp_.text
    if resp != "Sticker done.":
        return await message.edit(resp, del_in=5)
    result = await venom.get_inline_bot_results(
        bot_, f"quoteIT {message.from_user.id} -done"
    )
    await asyncio.gather(
        venom.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=result.query_id,
            result_id=result.results[0].id,
            reply_to_message_id=reply_.id,
        ),
        message.delete(),
    )


@venom.trigger("twit")
async def make_tweet(_, message: MyMessage):
    try:
        await venom.get_chat_member(-1001331162912, message.from_user.id)
    except BaseException:
        if message.from_user.id not in Config.TRUSTED_SUDO_USERS:
            return await message.edit(
                "First join **@UX_xplugin_support** and get approved by Kakashi."
            )
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to message...`", del_in=5)
    name_ = reply_.from_user.first_name
    username_ = "@" + reply_.from_user.username
    pfp_ = reply_.from_user.photo.big_file_id if reply_.from_user.photo else None
    text_ = (
        reply_.text
        if reply_.text and "-f" not in message.flags
        else message.filtered_input
    )
    fake_ = True if "-f" in message.flags else False
    bg_ = (26, 43, 60) if "-b" not in message.flags else (0, 0, 0)
    if not text_:
        return await message.edit("`Text not found...`", del_in=5)
    await message.edit("`Making tweet...`")
    bot_ = "QuoteIT_thebot"
    form_ = {
        "cmd": "TWEET_IT",
        "name": name_,
        "username": username_,
        "text": text_,
        "background": bg_,
        "fake": fake_,
    }
    json_ = json.dumps(form_, indent=4)
    if pfp_:
        down_ = await venom.download_media(pfp_)
        req_ = await venom.send_photo(bot_, down_, caption=json_)
        req_ = MyMessage.parse(req_)
        os.remove(down_)
    else:
        req_ = await venom.send_message(bot_, json_)
    try:
        response = await req_.wait(timeout=20, filters=(filters.bot))
    except TimeoutError:
        return await message.edit("`Bot didn't respond...`", del_in=5)
    resp = response.text
    if resp != "Sticker done.":
        return await message.edit(resp, del_in=5)
    result = await venom.get_inline_bot_results(
        bot_, f"tweetIT {message.from_user.id} -done"
    )
    await asyncio.gather(
        venom.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=result.query_id,
            result_id=result.results[0].id,
            reply_to_message_id=reply_.id,
        ),
        message.delete(),
    )

