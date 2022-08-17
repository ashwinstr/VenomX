# mark_read.py

from pyrogram.raw.functions.messages import read_mentions
from pyrogram.enums import ChatType

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name

DOT_ = Config.BULLET_DOT


help_ = Config.HELP[plugin_name(__name__)] = {'type': 'essents', 'commands': []}


###############################################################################################################################################


help_['commands'].append(
    {
        'command': 'markr',
        'flags': None,
        'usage': 'mark tags/mentions as read',
        'syntax': '{tr}markr',
        'sudo': False
    }
)

@venom.trigger('markr')
async def mark_read(_, message: MyMessage):
    " mark tags/mentions as read "
    chats_ = venom.get_dialogs()
    list_ = "<b>Chat mentions marked as read:</b> [<b>{}</b>]\n\n"
    total_ = 0
    async for one in chats_:
        if one.chat.type == ChatType.PRIVATE:
            continue
        if not one.unread_mentions_count:
            continue
        r = await venom.invoke(read_mentions.ReadMentions(peer=await venom.resolve_peer(one.chat.id)))
        list_ += (
            f"{DOT_} <b><u>{one.chat.title}</b></u>\n"
            f"    <b>Mentions:</b> <i>{one.unread_mentions_count}</i>\n"
            f"    <b>Marked read:</b> <i>Successful</i>\n\n"
        )
        total_ += 1
    if not total_:
        out_ = f"`No unread messages to mark read...`"
        del_in = 3
    else:
        out_ = list_.format(total_)
        del_in = -1
    await message.edit(out_, del_in=del_in)