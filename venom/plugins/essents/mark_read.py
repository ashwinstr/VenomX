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
        'about': 'mark tags/mentions as read'
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
        print(r)
        total_ += 1
    if not total_:
        out_ = f"{list_}<code>None.</code>"
    else:
        out_ = list_.format(total_)
    await message.edit(out_)
        