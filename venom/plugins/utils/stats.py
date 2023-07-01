"""Get Your Telegram Stats"""

# Was For USERGE-X
# Idea : https://github.com/kantek/.../kantek/plugins/private/stats.py
# Module By: github/code-rgb [TG - @DeletedUser420]
# Now Ported to Venom by Ryuk.

import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait, UserNotParticipant

from venom import MyMessage, venom, Config
from venom.helpers import plugin_name

#from userge.utils import mention_html, time_formatter


help_ = Config.HELP[plugin_name(__name__)] = {'type': 'utils', 'commands': []}


help_['commands'].append(
    {
        "command":"stats",
        "about": "Get Your Telegram Stats",
    },
)


@venom.trigger("stats")
async def get_stats_(_,message: MyMessage):
    """get info about your TG account"""
    #start = time.time()
    await message.edit(
        "`Collecting your Telegram Stats ...`\n"
        "<b>Please wait it will take some time</b>"
    )
    owner = await venom.get_me()
    u_mention = owner.first_name
    unread_mentions = 0
    unread_msg = 0
    private_chats = 0
    bots = 0
    users_ = 0
    groups = 0
    groups_admin = 0
    groups_creator = 0
    channels = 0
    channels_admin = 0
    channels_creator = 0
    try:
        async for dialog in venom.get_dialogs():
            unread_mentions += dialog.unread_mentions_count
            unread_msg += dialog.unread_messages_count
            chat_type = dialog.chat.type
            if chat_type in [ChatType.BOT,ChatType.PRIVATE]:
                private_chats += 1
                if chat_type == ChatType.BOT:
                    bots += 1
                else:
                    users_ += 1
            else:
                try:
                    checks_ = (await venom.get_chat_member(dialog.chat.id, owner.id)).status
                except UserNotParticipant:
                    pass
                if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    groups += 1
                    if checks_ == ChatMemberStatus.OWNER:
                        groups_creator += 1
                    if checks_ == ChatMemberStatus.ADMINISTRATOR:
                        groups_admin += 1
                else:  # Channel
                    channels += 1
                    if checks_ == ChatMemberStatus.OWNER:
                        channels_creator += 1
                    if checks_ == ChatMemberStatus.ADMINISTRATOR:
                        channels_admin += 1
    except FloodWait as e:
        await asyncio.sleep(e.value + 5)

    results = f"""
<b><u>Telegram Stats</u></b>
User:  <b>{u_mention}</b>

<b>Private Chats:</b> <code>{private_chats}</code><code>
    • Users: {users_}
    • Bots: {bots}</code>
<b>Groups:</b> <code>{groups}</code>
<b>Channels:</b> <code>{channels}</code>
<b>Admin in Groups:</b> <code>{groups_admin}</code><code>
    ★ Creator: {groups_creator}
    • Admin Rights: {groups_admin - groups_creator}</code>
<b>Admin in Channels:</b> <code>{channels_admin}</code><code>
    ★ Creator: {channels_creator}
    • Admin Rights: {channels_admin - channels_creator}</code>
<b>Unread Messages:</b> <code>{unread_msg}</code>
<b>Unread Mentions:</b> <code>{unread_mentions}</code>
"""
    #end = time.time()
    #results += f"\n<i>Process took: {time_formatter(end - start)}.</i>"
    await message.edit(results)

