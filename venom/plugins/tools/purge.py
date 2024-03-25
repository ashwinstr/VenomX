# PurgeME Ported from UX to VenomX by Ryuk.
# Purge taken from Plain-UB

import datetime

from venom import Config, MyMessage, venom

from venom.helpers import plugin_name

help_ = Config.HELP[plugin_name(__name__)] = {'type': 'help', 'commands': []}


@venom.trigger(cmd="purge")
async def purge_(_, message: MyMessage):
    start_message: int = 0
    if message.reply_to_message:
        start_message = message.replied.id
    if not start_message:
        return await message.reply("reply to a message")
    end_message: int = message.id
    messages: list[int] = [
        end_message,
        *[i for i in range(int(start_message), int(end_message))],
    ]
    await venom.delete_messages(
        chat_id=message.chat.id, message_ids=messages, revoke=True
    )



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
