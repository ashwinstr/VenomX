# pm_log.py
# on hold rn

import json
from time import time

from pyrogram import filters
from pyrogram.enums import ParseMode

from venom import venom, MyMessage, Config, Collection, test_print
from venom.helpers import plugin_name, CurrentTime, get_topics, create_topic, lock_topic

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}


async def _init() -> None:
    pm_tog = await Collection.TOGGLES.find_one({'_id': 'PM_TOG'})
    if pm_tog:
        Config.PM_TOG = pm_tog['switch']
    else:
        await Collection.TOGGLES.insert_one(
            {
                '_id': 'PM_TOG',
                'switch': Config.PM_TOG
            }
        )
    last_messages = await Collection.LAST_MESSAGES_LIST.find_one({'_id': 'PM_LAST_MESSAGES_LIST'})
    if last_messages:
        string_ = last_messages['dict']
        try:
            json_ = json.loads(string_)
            Config.PM_LAST_MESSAGES = json_
        except TypeError:
            await Collection.LAST_MESSAGES_LIST.delete_one(last_messages)
            await Collection.LAST_MESSAGES_LIST.insert_one(
                {
                    '_id': 'PM_LAST_MESSAGES_LIST',
                    'dict': Config.PM_LAST_MESSAGES
                }
            )
    else:
        await Collection.LAST_MESSAGES_LIST.insert_one(
            {
                '_id': 'PM_LAST_MESSAGES_LIST',
                'dict': Config.PM_LAST_MESSAGES
            }
        )
    Config.PM_LOG_TOPICS = await get_topics(venom, Config.PM_LOG_GROUP)


########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'pmlog',
        'flags': {
            '-c': 'check',
        },
        'usage': 'toggle pm log',
        'syntax': '{tr}pmlog',
        'sudo': False
    }
)


@venom.trigger('pmlog')
async def pm_log_toggle(_, message: MyMessage):
    """ toggle pm log """
    if not Config.PM_LOG_GROUP:
        return await message.edit("First add `PM_LOG_GROUP` in config...`", del_in=3)
    if '-c' in message.flags:
        switch_ = "ON" if Config.PM_TOG else "OFF"
        return await message.edit(f"PM_LOG switch is currently <b>{switch_}</b>.", del_in=5)
    Config.PM_TOG = False if Config.PM_TOG else True
    await Collection.TOGGLES.update_one(
        {'_id': 'PM_TOG'}, {'$set': {'switch': Config.PM_TOG}}, upsert=True
    )
    switch_ = "ON" if Config.PM_TOG else "OFF"
    await message.edit(f"PM_LOG switch is now <b>{switch_}</b>.", del_in=3)


########################################################################################################################

pm_log = filters.create(lambda _, __, m: Config.PM_TOG)

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'pmlognow',
        'flags': None,
        'usage': 'log stored pm messages',
        'syntax': '{tr}pmlognow',
        'sudo': False
    }
)


@venom.trigger('pmlognow')
async def pm_log_now(_, __):
    """ log latest messages """
    try:
        await venom.bot.send_message(Config.PM_LOG_GROUP, Config.PM_LOGS)
    except Exception as e:
        test_print(e)


########################################################################################################################

_private_filters = pm_log & (filters.incoming | filters.outgoing) & filters.private


@venom.on_message(_private_filters, group=-2)
@venom.on_edited_message(_private_filters, group=-1)
async def log_messages(_, message: MyMessage):
    """ log incoming message in topics """
    time_ = time()
    chat_ = message.chat.id
    first_name = message.chat.first_name
    if message.from_user.id != chat_:
        first_name = message.from_user.first_name
    topic_title = [one.title for one in Config.PM_LOG_TOPICS]
    topic_title_ids = [one.split(" - ")[1] for one in topic_title if len(one.split(" - ")) == 2]
    if chat_ not in Config.PM_LOGS.keys():
        Config.PM_LOGS[chat_] = ""
    if str(chat_) not in topic_title_ids:
        await create_topic(client=venom, channel=Config.PM_LOG_GROUP, title=f"{first_name} - {chat_}")
        Config.PM_LOG_TOPICS = await get_topics(venom, Config.PM_LOG_GROUP)
        latest_topic = Config.PM_LOG_TOPICS[0]
        await lock_topic(client=venom, channel=Config.PM_LOG_GROUP, id=latest_topic.id)
    logging_msg = Config.PM_LOGS[chat_] + f"""
--{first_name}--:
**{CurrentTime().default_format}** [{message.text}]({message.link})
"""
    Config.PM_MSG_LOGGED += 1
    if chat_ not in Config.PM_LAST_MESSAGES.keys():
        last_message = [
            one.top_message for one in Config.PM_LOG_TOPICS
            if len(one.title.split(" - ")) == 2 and one.title.split(" - ")[1] == str(chat_)
        ][0]
    else:
        last_message = Config.PM_LAST_MESSAGES[chat_]
    if len(logging_msg) >= 4096:
        Config.PM_MSG_LOGGED = 0
        msg = await venom.bot.send_message(chat_id=Config.PM_LOG_GROUP,
                                           text=Config.PM_LOGS[chat_],
                                           dis_preview=True,
                                           parse_mode=ParseMode.MARKDOWN,
                                           reply_to_message_id=last_message)
        Config.PM_LOGS[chat_] = ""
    elif Config.PM_MSG_LOGGED == 5 or time() - time_ >= 15:
        Config.PM_MSG_LOGGED = 0
        msg = await venom.bot.send_message(chat_id=Config.PM_LOG_GROUP,
                                           text=logging_msg,
                                           dis_preview=True,
                                           parse_mode=ParseMode.MARKDOWN,
                                           reply_to_message_id=last_message)
        Config.PM_LOGS[chat_] = ""
    else:
        Config.PM_LOGS[chat_] = logging_msg
        return
    Config.PM_LAST_MESSAGES[chat_] = msg.id
    str_ = json.dumps(Config.PM_LAST_MESSAGES)
    await Collection.LAST_MESSAGES_LIST.update_one(
        {'_id': 'PM_LAST_MESSAGES_LIST'},
        {'$set': {'dict': str_}},
        upsert=True
    )

########################################################################################################################

_group_filters = pm_log & filters.mentioned & filters.group
