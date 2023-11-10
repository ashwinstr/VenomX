# pm_guard.py

import asyncio
from pymongo.errors import DuplicateKeyError

from pyrogram import filters
from pyrogram.enums import MessagesFilter, ChatType

from venom import venom, MyMessage, Config, Collection
from venom.helpers import plugin_name, report_user


HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'security', 'commands': []}
CHANNEL = venom.getCLogger(__name__)
WELCOME_MSG = """
Hi <b>{}</b>,
This is <b>{}</b>'s userbot, VenomX.

You're messaging the owner without his/her consent, please wait for his/her reply and refrain from sending more than 4 messages.
Else you'll be blocked and reported for spamming.
Thank you.
"""

async def _init() -> None:
    found = await Collection.TOGGLES.find_one({'_id': 'PM_GUARD'})
    if found:
        Config.PM_GUARD = found['switch']
    else:
        Config.PM_GUARD = False
    async for one in Collection.ALLOWED_TO_PM.find():
        Config.ALLOWED_TO_PM.append(one['_id'])
    async for one in Collection.DISALLOWED_PM_COUNT.find():
        Config.DISALLOWED_PM_COUNT[one['_id']] = one['count']


########################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'pmguard',
        'flags': {
            '-c': 'check',
        },
        'usage': 'toggle pm_guard to secure your pm',
        'syntax': '{tr}pmguard [optional flag]',
        'sudo': False
    }
)


@venom.trigger('pmguard')
async def pm_guard(_, message: MyMessage):
    """ secure your PMs """
    if '-c' in message.flags:
        switch_ = "ON" if Config.PM_GUARD else "OFF"
        return await message.edit(f"<b>PM_GUARD</b> is currently <b>{switch_}</b>.", del_in=5)
    Config.PM_GUARD, switch_ = (False, "OFF") if Config.PM_GUARD else (True, "ON")
    await Collection.TOGGLES.update_one(
        {'_id': 'PM_GUARD'}, {'$set': {'switch': Config.PM_GUARD}}, upsert=True
    )
    await message.edit(f"<b>PM_GUARD</b> is now: <b>{switch_}</b>", del_in=5)


########################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'allow',
        'flags': None,
        'usage': 'allow user to pm you',
        'syntax': '{tr}allow [in PM] or [reply to user in group to allow PM]',
        'sudo': False
    }
)

@venom.trigger('allow')
async def allow_pm(_, message: MyMessage):
    """ allow user to pm you """
    if message.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
        reply_ = message.replied
        if not reply_:
            return await message.edit("`Reply to user to allow PM.`", del_in=5)
        if reply_.from_user.id in Config.ALLOWED_TO_PM:
            return await message.edit(f"`User {reply_.from_user.first_name} is already allowed to PM.`", del_in=5)
        Config.ALLOWED_TO_PM.append(reply_.from_user.id)
        await asyncio.gather(
            Collection.ALLOWED_TO_PM.insert_one({'_id': reply_.from_user.id}),
            message.edit(f"User <b>{reply_.from_user.first_name}</b> is now allowed to PM."),
            CHANNEL.log(f"User **{reply_.from_user.first_name}** is now **allowed** to PM.")
        )
    elif message.chat.type == ChatType.BOT:
        return
    elif message.chat.type == ChatType.PRIVATE:
        user_id = message.chat.id
        user_name = message.chat.first_name
        if user_id in Config.ALLOWED_TO_PM:
            return await message.edit(f"`User {user_name} is already allowed to PM.`", del_in=5)
        Config.ALLOWED_TO_PM.append(user_id)
        return await asyncio.gather(
            Collection.ALLOWED_TO_PM.insert_one({'_id': user_id}),
            message.edit(f"User <b>{user_name}</b> is now <b>allowed</b> to PM."),
            CHANNEL.log(f"User **{user_name}** is now **allowed** to PM.")
        )
    Config.DISALLOWED_PM_COUNT[message.from_user.id] = 0

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'nopm',
        'flags': None,
        'usage': 'disallow user to pm you',
        'syntax': '{tr}nopm [in PM] or [reply to user in group to disallow PM]',
        'sudo': False
    }
)

@venom.trigger('nopm')
async def dis_allow_pm(_, message: MyMessage):
    """ disallow user to pm you """
    if message.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
        reply_ = message.replied
        if not reply_:
            return await message.edit("`Reply to user to disallow PM.`", del_in=5)
        if reply_.from_user.id not in Config.ALLOWED_TO_PM:
            return await message.edit(f"`User {reply_.from_user.first_name} is already disallowed to PM.`", del_in=5)
        Config.ALLOWED_TO_PM.remove(reply_.from_user.id)
        await asyncio.gather(
            Collection.ALLOWED_TO_PM.delete_one({'_id': reply_.from_user.id}),
            message.edit(f"User <b>{reply_.from_user.first_name}</b> is now disallowed to PM.")
        )
    elif message.chat.type == ChatType.BOT:
        return
    elif message.chat.type == ChatType.PRIVATE:
        user_id = message.chat.id
        user_name = message.chat.first_name
        if user_id not in Config.ALLOWED_TO_PM:
            return await message.edit(f"`User {user_name} is already disallowed to PM.`", del_in=5)
        Config.ALLOWED_TO_PM.remove(user_id)
        return await asyncio.gather(
            Collection.ALLOWED_TO_PM.delete_one({'_id': user_id}),
            message.edit(f"User <b>{user_name}</b> is now <b>disallowed</b> to PM.")
        )

########################################################################################################################################################

PM_GUARD = filters.create(lambda _, __, ___: Config.PM_GUARD)
NOT_ALLOWED = filters.create(lambda _, __, m: (m.from_user and m.from_user.id not in Config.ALLOWED_TO_PM))


@venom.on_message(
    PM_GUARD
    & filters.private
    & NOT_ALLOWED
    & ~filters.bot
    & ~filters.me
    & ~filters.service,
    group=4
)
async def guard_(_, message: MyMessage):
    """ guard on duty """
    pm_by = message.from_user.id
    if pm_by not in Config.DISALLOWED_PM_COUNT.keys():
        disallowed_count = Config.DISALLOWED_PM_COUNT[pm_by] = 1
    else:
        disallowed_count = Config.DISALLOWED_PM_COUNT[pm_by] = Config.DISALLOWED_PM_COUNT[pm_by] + 1
    if disallowed_count == 1:
        pm_user = await venom.get_users(pm_by)
        await message.reply_photo(Config.PM_WELCOME_PIC, caption=WELCOME_MSG.format(pm_user.first_name, Config.ME.first_name))
    elif 1 < disallowed_count < 4:
        await message.reply(f"You have been warned!\n<b>Number of spam messages:</b> {disallowed_count}")
    elif disallowed_count == 4:
        await message.reply("<b>This is the last warning to you. Next message you'll be blocked and reported.</b>")
    elif disallowed_count >= 5:
        await message.reply("`Enough is ENOUGH!\nYou have been blocked and reported for spam!")
        await message.from_user.block()
        await report_user(pm_by, pm_by, message.id, "Unsolicited message...")
    await Collection.DISALLOWED_PM_COUNT.update_one(
        {'_id': pm_by}, {'$set': {'count': disallowed_count}}, upsert=True
    )


@venom.on_message(
    PM_GUARD
    & NOT_ALLOWED
    & filters.me
    & filters.private,
    group=2
)
async def auto_allow(_, message: MyMessage):
    """ automatic allow on first message """
    user_ = message.chat.id
    if user_ not in Config.DISALLOWED_PM_COUNT.keys():
        Config.ALLOWED_TO_PM.append(user_)
        try:
            await asyncio.gather(
                CHANNEL.log(f"User <b>{message.chat.id}</b> auto-approved to PM."),
                Collection.ALLOWED_TO_PM.insert_one({'_id': user_})
            )
        except DuplicateKeyError:
            pass
