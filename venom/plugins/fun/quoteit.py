# quoteit.py

import asyncio
import json
import os
import re
from sre_constants import error as sre_err

from pyrogram import filters
from pyrogram.errors import UserNotParticipant

from venom import Config, MyMessage, venom


@venom.trigger("qit")
async def quote_message(_, message: MyMessage):
    """ quote support in userbot """
    from_user_ = message.from_user.id
    flags_ = message.flags
    try:
        await venom.get_chat_member(-1001331162912, from_user_)
    except UserNotParticipant:
        if from_user_ not in Config.TRUSTED_SUDO_USERS:
            return await message.edit("First join **@UX_xplugin_support** and get approved.")
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
        reply_text = reply_msg.reply_to_message.text.splitlines()[0]
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
        down_ = await venom.both.download_media(pfp_, file_name=f"profile_pic_{name_}.jpg")
        req_ = await venom.send_photo(bot_, down_, caption=json_)
        req_ = MyMessage.parse(_, req_)
        os.remove(down_)
    else:
        req_ = await venom.send_message(bot_, json_)
    try:
        resp_ = await req_.wait(timeout=20, filters=filters.bot)
    except asyncio.TimeoutError:
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
            reply_to_message_id=message.id,
        ),
        message.delete(),
    )


@venom.trigger("twit")
async def make_tweet(_, message: MyMessage):
    try:
        await venom.get_chat_member(-1001331162912, message.from_user.id)
    except UserNotParticipant:
        if message.from_user.id not in Config.TRUSTED_SUDO_USERS:
            return await message.edit(
                "First join **@UX_xplugin_support** and get approved."
            )
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to message...`", del_in=5)
    name_ = reply_.from_user.first_name
    username_ = "@" + reply_.from_user.username
    pfp_ = reply_.from_user.photo.big_file_id if reply_.from_user.photo else None
    regex_it = True if "-r" in message.flags else False
    text_ = (
        reply_.text
        if (reply_.text or (reply_.text and regex_it)) and "-f" not in message.flags
        else message.filtered_input
    )
    if regex_it:
        regex_ = message.filtered_input
        text_ = send_sed(text_, regex_)
    fake_ = True if "-f" in message.flags or "-r" in message.flags else False
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
        down_ = await venom.both.download_media(pfp_, file_name=f"profile_pic_{username_}.png")
        req_ = await venom.send_photo(bot_, down_, caption=json_)
        req_ = MyMessage.parse(_, req_)
        os.remove(down_)
    else:
        req_ = await venom.send_message(bot_, json_)
    try:
        response = await req_.wait(timeout=20, filters=filters.chat([bot_]))
    except asyncio.TimeoutError:
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
            reply_to_message_id=message.id,
        ),
        message.delete(),
    )


DELIMITERS = ("/", ":", "|", "_")


def separate_sed(sed_string):
    """ Separate sed arguments. """

    if str(sed_string).endswith(" -n"):
        sed_string = sed_string.replace(" -n", "")
    else:
        sed_string = str(sed_string)
    if len(sed_string) < 1:
        return

    if sed_string[1] in DELIMITERS and sed_string.count(sed_string[1]) >= 1:
        delim = sed_string[1]
        start = counter = 2
        while counter < len(sed_string):
            if sed_string[counter] == r"\\":
                counter += 1
            elif sed_string[counter] == delim:
                replace = sed_string[start:counter]
                counter += 1
                start = counter
                break

            counter += 1

        else:
            return None

        while counter < len(sed_string):
            if (
                    sed_string[counter] == "\{2}"
                    and counter + 1 < len(sed_string)
                    and sed_string[counter + 1] == delim
            ):
                sed_string = sed_string[:counter] + sed_string[counter + 1:]
            elif (counter + 1) < len(sed_string) and (sed_string[counter] + sed_string[counter + 1]) == "\/":
                sed_string = sed_string.replace(sed_string[counter], "")
                counter += 1
            elif sed_string[counter] == delim:
                replace_with = sed_string[start:counter]
                counter += 1
                break

            counter += 1
        else:
            return replace, sed_string[start:], ""

        flags = ""
        if counter < len(sed_string):
            flags = sed_string[counter:]
        return replace, replace_with, flags.lower()
    return None


def send_sed(text_, regex):
    sed_result = separate_sed(regex)
    if sed_result:
        repl, repl_with, flags = sed_result
    else:
        return
    if sed_result:
        try:
            check = re.match(repl, text_, flags=re.IGNORECASE)
            if check and check.group(0).lower() == text_.lower():
                pass
            if "i" in flags and "g" in flags:
                text = re.sub(fr"{repl}", fr"{repl_with}", text_, flags=re.I).strip()
            elif "u" in flags and "g" in flags:
                repl_with = bytes(repl_with, "utf-8").decode('unicode_escape')
                text = re.sub(fr"{repl}", repl_with, text_).strip()
            elif "u" in flags and "i" in flags:
                repl_with = bytes(repl_with, "utf-8").decode('unicode_escape')
                text = re.sub(fr"{repl}", repl_with, text_, count=1, flags=re.I).strip()
            elif "i" in flags:
                text = re.sub(fr"{repl}", fr"{repl_with}", text_, count=1, flags=re.I).strip()
            elif "g" in flags:
                text = re.sub(fr"{repl}", fr"{repl_with}", text_).strip()
            elif "m" in flags:
                text = re.sub(fr"{repl}", fr"{repl_with}", text_.html, count=1).strip()
            elif "u" in flags:
                repl_with = bytes(repl_with, "utf-8").decode('unicode_escape')
                text = re.sub(fr"{repl}", repl_with, text_, count=1).strip()
            #            elif "e" in flags:
            #                text = re.sub(fr"{repl}", repl_with, to_fix, count=1).strip()
            else:
                text = re.sub(fr"{repl}", fr"{repl_with}", text_, count=1).strip()
        except sre_err as e:
            return f"ERROR: {e}"
        #            return await bot.send_message(message.chat.id, "**[Learn Regex](https://regexone.com)**")
        if text:
            return text
        return "ERROR !!!"


@venom.trigger('uni')
async def unicode_print(_, message: MyMessage):
    """ testing unicodes """
    link_ = message.replied.link if message.replied else message.link
