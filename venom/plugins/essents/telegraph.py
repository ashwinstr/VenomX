# telegraph.py

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name, post_tg_media, post_tg


HELP = Config.HELP[plugin_name(__name__)] = {'type': 'essents', 'commands': []}


########################################################################################################################

HELP['commands'].append(
    {
        'command': 'tgmedia',
        'flags': None,
        'about': 'upload media to telegraph',
        'sudo': True
    }
)


@venom.trigger('tgmedia')
async def tg_media(_, message: MyMessage):
    " upload media to telegraph "
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to media to upload...`")
    link_ = await post_tg_media(message)
    await message.edit(link_)


########################################################################################################################

HELP['commands'].append(
    {
        'command': 'tgtext',
        'flags': None,
        'about': 'post text to telegraph',
        'sudo': True
    }
)


@venom.trigger('tgtext')
async def tg_text(_, message: MyMessage):
    " post text to telegraph "
    replied = message.replied
    if not replied and not replied.text:
        return await message.edit("`Reply to text to post into telegraph.`")
    await message.edit("`Posting to telegraph...`")
    link_ =  post_tg("VenomX telagraph...", replied.text)
    await message.edit("[<b>Posted to telegra.ph</b>]({})".format(link_), dis_preview=True)