# tg_ids.py

from pyrogram.enums import ChatType
from pyrogram.errors import UserIdInvalid, UsernameInvalid, UsernameNotOccupied, PeerIdInvalid

from venom import venom, Config, MyMessage
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}

####################################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'ids',
        'flags': None,
        'about': 'get telegram ids',
        'syntax': '{tr}ids [input username or reply to user/channel forward]',
        'sudo': True
    }
)

@venom.trigger('ids')
async def id_s(_, message: MyMessage):
    " get telegram ids "
    out_ = "<b>Looking for</b> `{}`\n\n<b>User ID:</b> `{}`\n"
    target = message.input_str
    chat_ = message.chat.id
    reply_ = message.replied
    if message.chat.type == ChatType.PRIVATE:
        looking_for = message.chat.first_name if not reply_ else reply_.from_user.first_name
    else:
        looking_for = message.from_user.first_name if not reply_ else reply_.from_user.first_name
    if reply_ and reply_.forward_from:
        out_ += f"<b>Forward from:</b> `{reply_.forward_from.id}`\n"
    out_ += f"<b>Chat ID:</b> `{chat_}`\n"
    if reply_ and reply_.forward_from_chat:
        out_ += f"<b>Forward from chat:</b> `{reply_.forward_from_chat.id}`\n"
    msg_id = message.id if not reply_ else reply_.id
    out_ += f"<b>Message ID:</b> `{msg_id}`"
    if not target:
        user_id = message.from_user.id if not reply_ else reply_.from_user.id
    else:
        user_ = "@" + target.lstrip("@")
        try:
            user_ = await venom.get_users(user_)
            user_id = user_.id
        except (UserIdInvalid, UsernameNotOccupied, UsernameInvalid, PeerIdInvalid):
            user_id = "`ERROR`"
    await message.edit(out_.format(looking_for, user_id))