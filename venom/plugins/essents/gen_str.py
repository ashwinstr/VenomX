# gen_str.py

import asyncio
import traceback

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import (
    FloodWait,
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded
)

from venom import venom, MyMessage, Config

CHANNEL = venom.getCLogger(__name__)


@venom.bot.on_message(
    filters.private
    & filters.user(Config.OWNER_ID)
    & filters.text
    & filters.command('genstr', prefixes=Config.CMD_TRIGGER),
    group=2
)
async def generate_str(_, m):
    " generate session string in bot mode "
    message: MyMessage = MyMessage.parse(m)
    await message.reply("Are you certain you want to generate session_string?\nReply `y` to continue.")
    try:
        resp = await message.wait()
    except asyncio.TimeoutError:
        return await message.reply("`Response not found !!!\nTerminating process...`")
    if resp.text.upper() != 'YES' and resp.text.upper() != 'Y':
        return await message.reply("`Wrong response.\nTerminating the process...`")
    api_id = Config.API_ID
    api_hash = Config.API_HASH
    num = (await venom.get_users(Config.OWNER_ID)).phone_number
    if num is None:
        return await message.reply("`First allow me in phone number privacy setting...`")
    process_ = await resp.reply("`Generating session string...`")
    try:
        client = Client(name="MyAccount", api_hash=api_hash, api_id=api_id)
    except Exception as e:
        return await process_.edit(f"<b>ERROR:</b> `{e}`")
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    except Exception as e:
        return await process_.edit(e)
    await process_.edit("`Successfully connected to client.`")
    try:
        code = await client.send_code(num)
        await asyncio.sleep(1)
    except FloodWait as e:
        return await process_.edit(f"`You have floodwait of {e.x} seconds.`", del_in=5)
    except ApiIdInvalid:
        return await process_.edit("`API_ID and API_HASH are invalid.`", del_in=5)
    except PhoneNumberInvalid:
        return await process_.edit("`Your phone number is invalid.`", del_in=5)
    try:
        msg_ = (
            "`An otp is sent to your phone number.`\n"
            "Please enter otp in `1 2 3 4 5` format."
        )
        otp = await process_.ask(msg_, timeout=300)
    except TimeoutError:
        return await process_.edit("`Time limit reached of 5 min.\nPlease try again later.`", del_in=5)
    if otp.text == f"{Config.CMD_TRIGGER}cancel":
        return await client.disconnect()
    otp_code = otp.text
    try:
        await client.sign_in(num, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        return await otp.reply("`Invalid code.`")
    except PhoneCodeExpired:
        return await otp.reply("`Code is expired.`")
    except SessionPasswordNeeded:
        try:
            two_step_code = await message.ask( 
                f"`This account have two-step verification code.\nPlease enter your second factor authentication code.`\nPress {Config.CMD_TRIGGER}cancel to cancel.",
                timeout=300
            )
        except TimeoutError:
            return await otp.reply("`Time limit reached of 5 min.\nTry again.`")
        if two_step_code.text == f"{Config.CMD_TRIGGER}cancel":
            return await client.disconnect()
        new_code = two_step_code.text
        await two_step_code.delete()
        try:
            await client.check_password(new_code)
        except Exception as e:
            return await two_step_code.reply(f"**ERROR:** `{str(e)}`")
    except Exception:
        return await otp.reply(f"**ERROR:** `{traceback.format_exc()}`")
    session_string = await client.export_session_string()
    await client.send_message("me", f"#PYROGRAM #STRING_SESSION @UX_xplugin_support\n\n```{session_string}```")

    text = "`String session is successfully generated.\nClick on button Below.`"
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Click Me", url=f"tg://openmessage?user_id={Config.OWNER_ID}")]]
    )
    await message.reply(text, reply_markup=reply_markup)
        