# gen_str.py
# big thanks to the dev who made it, Krishna

import asyncio
import traceback

from pyrogram import filters, Client
from pyrogram.errors import (
    FloodWait,
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from venom import venom, MyMessage, Config, plugin_name, SecureConfig

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'essents', 'commands': []}
CHANNEL = venom.getCLogger(__name__)


HELP_['commands'].append(
    {
        'command': 'genstr',
        'flags': None,
        'usage': 'Generate Session-string with bot mode...',
        'syntax': '{tr}genstr',
        'sudo': False
    }
)


@venom.bot.on_message(
    filters.private
    & filters.user(Config.OWNER_ID)
    & filters.text
    & filters.command('genstr', prefixes=Config.CMD_TRIGGER),
    group=2
)
async def generate_str(_, message: MyMessage):
    """ generate session string in bot mode """
    await message.reply("Are you certain you want to generate session_string?\nReply `y` to continue.")
    try:
        resp = await message.wait_for()
    except asyncio.TimeoutError:
        return await message.reply("`Response not found !!!\nTerminating process...`")
    if resp.text.upper() != 'YES' and resp.text.upper() != 'Y':
        return await message.reply("`Wrong response.\nTerminating the process...`")
    secure_vars = SecureConfig()
    api_id = secure_vars.API_ID
    api_hash = secure_vars.API_HASH
    num = (await venom.get_users(Config.OWNER_ID)).phone_number
    if num is None:
        return await message.reply("`First allow me(bot) in phone number privacy setting...`")
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
        return await process_.edit(str(e))
    await process_.edit("`Successfully connected to client.`")
    try:
        code = await client.send_code(num)
        await asyncio.sleep(1)
    except FloodWait as e:
        return await process_.edit(f"`You have FloodWait of {e.value} seconds.`", del_in=5)
    except ApiIdInvalid:
        return await process_.edit("`API_ID and API_HASH are invalid.`", del_in=5)
    except PhoneNumberInvalid:
        return await process_.edit("`Your phone number is invalid.`", del_in=5)
    try:
        msg_ = (
            "`An otp is sent to your phone number.`\n"
            "Please enter otp in `1 2 3 4 5` format."
        )
        ask_otp = await process_.reply(msg_)
        otp = await ask_otp.wait_for(timeout=300)
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
            ask_two_step_code = await otp.reply(
                f"`This account have two-step verification code.\nPlease enter your second factor authentication code.`"
                f"\nPress {Config.CMD_TRIGGER}cancel to cancel."
            )
            two_step_code = await ask_two_step_code.wait_for(300)
        except TimeoutError:
            return await otp.reply("`Time limit reached of 5 min.\nTry again.`")
        if two_step_code.text == f"{Config.CMD_TRIGGER}cancel":
            return await client.disconnect()
        new_code = two_step_code.text
        await two_step_code.delete()
        try:
            await client.check_password(new_code)
        except BaseException as e:
            return await two_step_code.reply(f"**ERROR:** `{str(e)}`")
    except BaseException:
        return await otp.reply(f"**ERROR:** `{traceback.format_exc()}`")
    session_string = await client.export_session_string()
    await client.send_message("me", f"#PYROGRAM #STRING_SESSION @VenomX_support\n\n`{session_string}`")

    text = "`String session is successfully generated.\nClick on button Below.`"
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Click Me", url=f"tg://openmessage?user_id={Config.OWNER_ID}")]]
    )
    await message.reply(text, reply_markup=reply_markup)
