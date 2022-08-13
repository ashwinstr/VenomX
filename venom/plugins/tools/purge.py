# Ported from UX to VenomX by Ryuk.

import datetime

from pyrogram.errors import MessageDeleteForbidden

from venom import Config, MyMessage, venom

from venom.helpers import plugin_name

help_ = Config.HELP[plugin_name(__name__)] = {'type': 'help', 'commands': []}


help_['commands'].append(
    {
        "command":"purge",
        "about": "purge messages",
        "flags": {
            "-u": "get user_id from replied message",
            "-l": "message limit : max 100",
        },
        "syntax": "\n   reply {tr}purge to the start message to purge.\n"
            "\n   use {tr}purge [user_id | user_name] to purge messages from that user or use flags\n"
            "\n   {tr}purge {tr}purge -u\n",
        "sudo": True,
    },
)

@venom.trigger(
    "purge"
)
async def purge_(_,message: MyMessage):
    """purge from replied message"""
    await message.edit("`purging ...`")
    start_m = message.id
    from_user_id = None
    end_message = 0
    if "l" in message.flags:
        limit = int(message.flags["l"])
        limit = min(limit, 100)
        end_message = message.id - limit
    if message.reply_to_message:
        end_message = message.reply_to_message.id
        if "u" in message.flags:
            from_user_id = message.reply_to_message.from_user.id
    if not end_message:
        await message.edit("invalid start message!")
        return
    list_of_messages = []
    purged_messages_count = 0

    async def handle_msg(a_message):
        nonlocal list_of_messages, purged_messages_count
        if (
            from_user_id
            and a_message
            and a_message.from_user
            and a_message.from_user.id == from_user_id
        ):
            list_of_messages.append(a_message.id)
        if not from_user_id:
            list_of_messages.append(a_message.id)
        if len(list_of_messages) >= 100:
            try:
                await message._client.delete_messages(
                    chat_id=message.chat.id, message_ids=list_of_messages
                )
            except MessageDeleteForbidden:
                return
            purged_messages_count += len(list_of_messages)
            list_of_messages = []

    start_t = datetime.datetime.now()
    if message._client.isbot:
        for a_message in await message._client.get_messages(
            chat_id=message.chat.id,
            replies=0,
            message_ids=range(start_message, message.message_id),
        ):
            await handle_msg(a_message)
    else:
        async for a_message in message._client.get_chat_history(
            chat_id=message.chat.id, limit=None, offset_id=start_m
        ):
            if end_message == a_message.id:
                await handle_msg(a_message)
                break
            await handle_msg(a_message)
    if list_of_messages:
        try:
            await message._client.delete_messages(
                chat_id=message.chat.id, message_ids=list_of_messages
            )
        except MessageDeleteForbidden:
            return
        purged_messages_count += len(list_of_messages)
    end_t = datetime.datetime.now()
    time_taken_s = (end_t - start_t).seconds
    out = f"<u>purged</u> {purged_messages_count} messages in {time_taken_s} seconds."
    await message.edit(out, del_in=3)



############################################################################################################################################



help_['commands'].append(
        {
        "command": "purgeme",
        "about": "purge messages from yourself",
        "syntax": "{tr}purgeme [number]\n"
                "{tr}purgeme 10",
    },
)


@venom.trigger(
    "purgeme"
)
async def purgeme_(_,message: MyMessage):
    """purge given no. of your messages"""
    await message.edit("`purging ...`")
    numb_ = message.text.split(" ")
    if not (len(numb_) >1 and numb_[1].isdigit):
        return await message.edit(
            "Provide a valid number of message to delete", del_in=3
        )
    start_t = datetime.datetime.now()
    number = min(int(numb_[1]), 100)
    mid = message.id
    msg_list = []
    # https://t.me/pyrogramchat/266224
    # search_messages takes some minutes to index new messages
    # so using iter_history to get messages newer than 5 mins.
    old_msg = start_t - datetime.timedelta(minutes=5)

    async for msg in venom.search_messages(
        message.chat.id, "", limit=number, from_user="me"
    ):
        msg_list.append(msg.id)

    async for new_msg in venom.get_chat_history(message.chat.id, offset_id=mid, offset=0):
        if new_msg.from_user.is_self:
            msg_list.append(new_msg.id)
        if old_msg > new_msg.date or (msg_list and (msg_list[-1] > new_msg.id)):
            break

    # https://stackoverflow.com/questions/39734485/python-combining-two-lists-and-removing-duplicates-in-a-functional-programming
    del_list = list(set(msg_list))
    if mid in del_list:
        del_list.remove(mid)
    del_list.reverse()
    del_list_ = del_list[:number]

    await venom.delete_messages(message.chat.id, message_ids=del_list_)

    end_t = datetime.datetime.now()
    time_taken_s = (end_t - start_t).seconds
    out = f"<u>purged</u> {len(del_list_)} messages in {time_taken_s} seconds."
    await message.edit(out, del_in=3)
