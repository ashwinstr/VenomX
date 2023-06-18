# html_parse.py
from asyncio import gather
from re import compile as comp_regex

from pyrogram.enums import ParseMode

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name, get_file_id

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}
BTN_REGEX = comp_regex(
    r"\[([^\[]+?)](\[buttonurl:(?:/{0,2})(.+?)(:same)?]|\(buttonurl:(?:/{0,2})(.+?)(:same)?\))"
)

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'parse',
        'flags': None,
        'usage': 'parse message with html',
        'syntax': '{tr}parse [reply to message]',
        'sudo': True
    }
)


@venom.trigger('parse1')
async def html_parse(_, message: MyMessage):
    """ parse message with html """
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to message to parse...`", del_in=5)
    await message.edit(reply_.text, parse_mode=ParseMode.HTML)


@venom.trigger('parse')
async def markdown_parser(_, message: MyMessage):
    """ parser """
    await message.edit("<code>Creating an Inline Button...</code>")
    reply = message.replied
    msg_content = None
    media_valid = False
    media_id = 0
    if reply:
        media_valid = bool(get_file_id(reply))

    if message.input_str:
        msg_content = message.input_str
        if media_valid:
            media_id = (await reply.forward(Config.LOG_CHANNEL_ID)).id

    elif reply:
        if media_valid:
            media_id = (await reply.forward(Config.LOG_CHANNEL_ID)).id
            msg_content = reply.caption.html if reply.caption else None
        elif reply.text:
            msg_content = reply.text.html

    if not msg_content:
        return await message.edit("`Content not found...`", del_in=5)

    rnd_id = venom.rnd_id()
    msg_content = check_brackets(msg_content)
    await message.edit(msg_content, parse_mode=ParseMode.DEFAULT)


def check_brackets(text: str):
    unmatch = BTN_REGEX.sub("", text)
    textx = ""
    for m in BTN_REGEX.finditer(text):
        if m.group(3):
            textx += m.group(0)
        elif m.group(5):
            textx += f"[{m.group(1)}][buttonurl:{m.group(5)}{m.group(6) or ''}]"
    return unmatch + textx