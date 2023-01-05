# pastes.py

from venom import venom, MyMessage, Config, plugin_name
from venom.helpers import paste_it

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'paste',
        'flags': None,
        'usage': 'Paste text to pasty.lus',
        'syntax': '{tr}paste [reply to document] or [input]',
        'sudo': True
    }
)


@venom.trigger('paste')
async def past_es(_, message: MyMessage):
    """ paste text to pasty.lus """
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to text...`", del_in=5)
    if not reply_.text and not reply_.caption and not reply_.document:
        return await message.edit("`Reply to text message or document...`", del_in=5)
    link_ = await paste_it(msg_content=message)
    if not link_:
        return await message.edit("`Message type not supported...`", del_in=5)
    await message.edit(f"Pasted to <b>PastyLus</b>\n<b>Link:</b> [URL]({link_})")