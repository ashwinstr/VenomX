# html_parse.py

from pyrogram.enums import ParseMode

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}

###########################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'parse',
        'flags': None,
        'usage': 'parse message with html',
        'syntax': '{tr}parse [reply to message]',
        'sudo': True
    }
)

@venom.trigger('parse')
async def html_parse(_, message: MyMessage):
    " parse message with html "
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to message to parse...`", del_in=5)
    await message.edit(reply_.text, parse_mode=ParseMode.HTML)

###########################################################################################################################################

""" HELP_['commands'].append(
    {
        'command': 'noformat',
        'flags': {
            '-m': 'return without markdown',
        },
        'usage': 'return replied message without html/markdown format',
        'syntax': '{tr}noformat [reply to message]',
        'sudo': True
    }
)

@venom.trigger('noformat')
async def no_format(_, message: MyMessage):
    " return replied message without html/markdown format "
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to message to parse...`", del_in=5)
    await message.edit(reply_.text) """