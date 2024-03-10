# fbans.py

import asyncio
import traceback
from asyncio.exceptions import TimeoutError

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait, PeerIdInvalid, UserBannedInChannel, UsernameInvalid, MessageIdInvalid

from venom import venom, MyMessage, Config, Collection
from venom.helpers import plugin_name, extract_id, report_user, user_friendly

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'security', 'commands': []}
CHANNEL = venom.getCLogger(__name__)
TOGGLES = Collection.TOGGLES
FED_LIST = Collection.FED_LIST


########################################################################################################################


async def _init() -> None:
    found = await TOGGLES.find_one({"_id": "F_DEL"})
    Config.F_DEL = found["switch"] if found else False
    tog = await TOGGLES.find_one({"_id": "FBAN_TAG"})
    if tog:
        Config.FBAN_TAG = tog["switch"]
    else:
        await TOGGLES.insert_one(
            {
                '_id': 'FBAN_TAG',
                'switch': False
            }
        )
        Config.FBAN_TAG = False


HELP_['commands'].append(
    {
        'command': 'fban_tag',
        'flags': {
            "-c": "check"
        },
        'usage': "enable/disable fbanner's tag",
        'syntax': '{tr}fban_tag',
        'sudo': False
    }
)


@venom.trigger('fban_tag')
async def fban_sudo_tags(_, message: MyMessage):
    """ Enable/disable fbanner's tag """
    if "-c" in message.flags:
        switch = "ON" if Config.FBAN_TAG else "OFF"
        return await message.edit(f"The switch is currently <b>{switch}</b>.", del_in=5)
    if Config.FBAN_TAG:
        Config.FBAN_TAG = False
        await message.edit("Fban tags are now <b>disabled</b>.", del_in=5)
    else:
        Config.FBAN_TAG = True
        await message.edit("Fban tags are <b>enabled</b>.", del_in=5)
    await TOGGLES.update_one(
        {"_id": "FBAN_TAG"}, {"$set": {"data": Config.FBAN_TAG}}, upsert=True
    )

########################################################################################################################


HELP_['commands'].append(
    {
        'command': 'f_del',
        'flags': {
            "-c": "check"
        },
        'usage': "toggle auto-delete fban confirmation",
        'syntax': '{tr}f_del',
        'sudo': False
    }
)


@venom.trigger('f_del')
async def f_delete(_, message: MyMessage):
    if "-c" in message.flags:
        out_ = "ON" if Config.F_DEL else "OFF"
        return await message.edit(f"Fban confirmation auto-delete : <b>{out_}</b>.", del_in=5)
    Config.F_DEL = False if Config.F_DEL else True
    await TOGGLES.update_one(
        {"_id": "F_DEL"}, {"$set": {"switch": Config.F_DEL}}, upsert=True
    )
    out_ = "ON" if Config.F_DEL else "OFF"
    await message.edit(f"Fban confirmation auto-delete : <b>{out_}</b>.")

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'addf',
        'flags': None,
        'usage': "Add a chat to fed list",
        'syntax': '{tr}addf [input chat id else current chat is default]',
        'sudo': False
    }
)


@venom.trigger('addf')
async def addfed_(_, message: MyMessage):
    """ Adds current chat to connected Feds. """
    name = message.input_str or message.chat.title
    chat_id = message.chat.id
    found = await FED_LIST.find_one({"_id": chat_id})
    if found:
        await message.edit(
            f"Chat __ID__: `{chat_id}`\nFed: **{found['fed_name']}**\n\nAlready exists in Fed List !",
            del_in=5,
        )
        return
    await FED_LIST.insert_one({"_id": chat_id, "fed_name": name})
    msg_ = f"__ID__ `{chat_id}` added to Fed: **{name}**"
    await message.edit(msg_, del_in=5)
    await CHANNEL.log(msg_)

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'delf',
        'flags': {
            '-all': 'Remove all the feds from fedlist',
        },
        'usage': "remove chat/s from fed list",
        'syntax': '{tr}delf [input chat id else current chat is default]',
        'sudo': False
    }
)


@venom.trigger('delf')
async def delfed_(_, message: MyMessage):
    """ Removes current chat from connected Feds. """
    if "-all" in message.flags:
        admin_ = message.from_user.id
        reg_ = filters.regex("^(?i)(yes|y)$")
        try:
            ask_ = await message.edit("Are you SURE? Reply 'y' or 'yes' to confirm.")
            resp = await ask_.wait(filters=(reg_ & filters.user([admin_, Config.OWNER_ID])))
        except TimeoutError:
            return await message.edit("`Reply not found... Aborting.`", del_in=5)
        if resp.text.upper() not in ["Y", "YES"]:
            return await message.edit("`Aborting...`", del_in=5)
        return await asyncio.gather(
            FED_LIST.drop(),
            CHANNEL.log("<b>Deleted all groups from FED_LIST.</b>"),
            ask_.edit("<b>FED_LIST cleared.</b>")
        )
    try:
        chat_ = await venom.get_chat(message.input_str or message.chat.id)
        chat_id = chat_.id
    except (PeerIdInvalid, IndexError):
        chat_id = message.input_str
        id_ = chat_id.replace("-", "")
        if not id_.isdigit() or not chat_id.startswith("-"):
            return await message.edit("Provide a valid chat ID...", del_in=5)
    out = f"Chat ID: {chat_id}\n"
    found = await FED_LIST.find_one({"_id": int(chat_id)})
    if found:
        msg_ = out + f"Successfully removed Fed: **{found['fed_name']}**"
        await message.edit(msg_, del_in=5)
        await FED_LIST.delete_one(found)
    else:
        return await message.edit(
            out + "**Does't exist in your Fed List !**", del_in=5
        )
    await CHANNEL.log(msg_)

########################################################################################################################

HELP_["commands"].append(
    {
        'command': 'fban',
        'flags': None,
        'usage': 'fban users',
        'syntax': '{tr}fban [reply to user or provide user ID] [reason]',
        'sudo': True
    }
)


@venom.trigger('fban')
async def fban_(_, message: MyMessage):
    """ Bans a user from connected Feds. """
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}</b>"]
    PROOF_CHANNEL = Config.FBAN_LOG_CHANNEL if Config.FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
    input_ = message.filtered_input
    await message.edit(fban_arg[0])
    sudo_ = False
    if (
        message.from_user.id in Config.SUDO_USERS
        or message.from_user.id in Config.TRUSTED_SUDO_USERS
    ):
        sudo_ = True
    if not message.reply_to_message:
        split_ = input_.split(" ", 1)
        user = split_[0]
        if not user.isdigit() and not user.startswith("@"):
            user = extract_id(message.text)
        if len(split_) == 2:
            reason = split_[1]
        else:
            reason = "not specified"
    else:
        user = message.reply_to_message.from_user.id
        reason = input_
    if user is None:
        return await message.edit("Provide a user ID or reply to a user...", del_in=5)
    try:
        user_ = await venom.get_users(user)
        user = user_.id
    except (PeerIdInvalid, IndexError, UsernameInvalid):
        pass
    if (
        user in Config.SUDO_USERS
        or user in Config.TRUSTED_SUDO_USERS
        or user == Config.OWNER_ID
        or user == (await venom.get_me()).id
    ):
        if not input_:
            await message.edit("Can't fban replied user, give user ID...", del_in=7)
            return
        user = input_.split()[0]
        reason = input_.split()[1:]
        reason = " ".join(reason)
        try:
            user_ = await venom.get_users(user)
            user = user_.id
        except (PeerIdInvalid, IndexError, UsernameInvalid):
            d_err = f"Failed to detect user **{user}**, fban might not work..."
            await message.edit(f"{d_err}\nType `y` to continue.")
            await CHANNEL.log(d_err)
            try:
                resp = await venom.listen(message.chat.id, filters=(filters.user(message.from_user.id)))
            except asyncio.TimeoutError:
                return await message.edit(
                    f"`Fban terminated...\nReason: Response timeout.`"
                )
            if resp.text == "y":
                pass
            else:
                return await message.edit(
                    f"`Fban terminated...\nReason: User didn't continue.`"
                )
        if (
            user in Config.SUDO_USERS
            or user in Config.TRUSTED_SUDO_USERS
            or user == Config.OWNER_ID
            or user == (await venom.get_me()).id
        ):
            return await message.edit(
                "Can't fban user that exists in SUDO or OWNERS...", del_in=7
            )
    try:
        user_ = await venom.get_users(user)
        u_link = user_.mention
        u_id = user_.id
    except PeerIdInvalid:
        u_link = user
        u_id = user
    failed = []
    total = 0
    reason = reason or "Not specified."
    await message.edit(fban_arg[1])
    once_ = True
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["_id"])
        try:
            user = f"<a href='tg://user?id={user}'>{user}</a>" if isinstance(user, int) else user
            send_ = await venom.send_message(chat_id, f"/fban {user} {reason}")
            response = await send_.wait(filters=(filters.user([609517172, 2059887769]) & ~filters.service))
            resp = response.text
            if not (
                ("New FedBan" in resp)
                or ("starting a federation ban" in resp)
                or ("start a federation ban" in resp)
                or ("FedBan Reason update" in resp)
            ):
                failed.append(f"{data['fed_name']}  \n__ID__: `{data['_id']}`")
        except UserBannedInChannel:
            pass
        except FloodWait as f:
            await asyncio.sleep(f.value + 3)
        except BaseException:
            if once_:
                await CHANNEL.log(traceback.format_exc())
                once_ = False
            failed.append(data["fed_name"])
    if total == 0:
        return await message.edit(
            f"You don't have any feds connected!\nSee {Config.CMD_TRIGGER}help addf for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Fbanned in `{total}` feds."
    msg_ = (
        fban_arg[3].format(u_link)
        + f"\n**ID:** <code>{u_id}</code>\n**Reason:** {reason}\n**Status:** {status}\n"
    )
    if sudo_:
        msg_ += f"**By:** {message.from_user.mention}"
    del_ = 3 if "-d" in message.flags or Config.F_DEL else -1
    await message.edit(msg_, del_in=del_)
    await venom.send_message(int(PROOF_CHANNEL), msg_)

########################################################################################################################

HELP_["commands"].append(
    {
        'command': 'fbanp',
        'flags': {
            '-r': 'remote fban, use with direct proof link',
            '-test': "for testing purpose, won't report the user"
        },
        'usage': 'fban users with proof',
        'syntax': '{tr}fbanp [reply to proof] [reason]',
        'sudo': True
    }
)


@venom.trigger('fbanp')
async def fban_p(_, message: MyMessage):
    """ Fban user from connected feds with proof. """
    flags_ = message.flags
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}{}</b>"]
    d_err = ("Failed to detect user **{}**, fban might not work...",)
    if not Config.FBAN_LOG_CHANNEL:
        await message.edit(
            "Add <code>FBAN_LOG_CHANNEL</code> to forward the proofs...", del_in=5
        )
        return
    try:
        channel_ = await venom.get_chat(int(Config.FBAN_LOG_CHANNEL))
    except BaseException:
        return await message.edit(
            f"`The FBAN_LOG_CHANNEL ID provided ('{Config.FBAN_LOG_CHANNEL}') is invalid, enter correct one.`",
            del_in=5,
        )
    if channel_.username is None or channel_.type != ChatType.CHANNEL:
        return await message.edit(
            "Proof channel should be a <b>channel</b> and should be <b>public</b> for this command to work...",
            del_in=5,
        )
    sudo_ = False
    if (
        message.from_user.id in Config.SUDO_USERS
        or message.from_user.id in Config.TRUSTED_SUDO_USERS
    ):
        sudo_ = True
    if "-r" in message.flags:
        link_ = message.filtered_input
        link_split = link_.split()
        link_ = link_split[0]
        try:
            reason = " ".join(link_split[1:])
        except IndexError:
            reason = "Not specified"
        try:
            user_and_message = link_.split("/")
            chat_id = user_and_message[-2]
            if chat_id.isdigit():
                chat_id = "-100" + str(chat_id)
                chat_id = int(chat_id)
            else:
                chat_ = await venom.get_chat(chat_id)
                chat_id = chat_.id
            msg_id = int(user_and_message[-1])
        except BaseException:
            await message.edit(
                "`Provide a proper spam message link to report...`", del_in=5
            )
            return
        try:
            msg_en = await venom.get_messages(chat_id, int(msg_id))
            user = msg_en.from_user.id
            proof = msg_en.id
        except MessageIdInvalid:
            await message.edit(
                "`Provide a proper spam message link to report...`", del_in=5
            )
            return
        input_ = ""
    else:
        reply = message.reply_to_message
        if not reply:
            await message.edit("Please reply to proof...", del_in=7)
            return
        chat_id = message.chat.id
        user = reply.from_user.id
        input_ = message.filtered_input
        reason = input_
        msg_en = reply
        proof = msg_en.id
    fps = True
    if (
        user_friendly(user)
        or user == (await venom.get_me()).id
    ):
        fps = False
        if not input_:
            await message.edit(
                "Can't fban replied/specified user because of them being SUDO_USER or OWNER, give user ID...",
                del_in=5,
            )
            return
        split_ = input_.split(" ", 1)
        user = split_[0]
        if not user.isdigit() and not user.startswith("@"):
            user = extract_id(message.text)
        try:
            user_ = await venom.get_users(user)
            user = user_.id
        except (PeerIdInvalid, IndexError, UsernameInvalid):
            d_err = f"Failed to detect user **{user}**, fban might not work..."
            await message.edit(d_err, del_in=5)
            await CHANNEL.log(d_err)
        try:
            reason = split_[1]
        except IndexError:
            reason = "not specified"
        if (
            user_friendly(user)
            or user == (await venom.get_me()).id
        ):
            return await message.edit(
                "Can't fban user that exists in SUDO or OWNERS...", del_in=5
            )
    try:
        user_ = await venom.get_users(user)
        u_link = user_.mention
        u_id = user_.id
    except PeerIdInvalid:
        u_link = user
        u_id = user
    await message.edit(fban_arg[0])
    failed = []
    r_update = []
    total = 0
    await message.edit(fban_arg[1])
    log_fwd = await venom.forward_messages(
        int(Config.FBAN_LOG_CHANNEL),
        from_chat_id=chat_id,
        message_ids=proof,
    )
    reason = reason or "Not specified"
    reason += " || {" + log_fwd.link + "}"
    if fps and '-test' not in flags_:
        await report_user(
            chat=chat_id,
            user_id=user,
            msg_id=proof,
            reason=reason,
        )
        reported = "</b> and <b>reported "
    else:
        if '-test' in flags_:
            reported = "</b> and <b>tested with "
        else:
            reported = ""
    once_ = True
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["_id"])
        try:
            user = f"<a href='tg://user?id={user}'>{user}</a>" if isinstance(user, int) else user
            send_ = await venom.send_message(
                chat_id,
                f"/fban {user} {reason}",
                dis_preview=True
            )
            response = await send_.wait(filters=(filters.user([609517172, 2059887769]) & ~filters.service))
            resp = response.text
            if not (
                ("New FedBan" in resp)
                or ("FedBan reason updated" in resp)
                or ("starting a federation ban" in resp)
                or ("start a federation ban" in resp)
            ):
                failed.append(f"{data['fed_name']}  \n__ID__: {data['_id']}")
            elif "FedBan Reason update" in resp:
                r_update.append(f"{data['fed_name']} - <i>Reason updated</i>")
        except UserBannedInChannel:
            pass
        except FloodWait as f:
            await asyncio.sleep(f.value + 3)
        except BaseException as e:
            if once_:
                await CHANNEL.log(f"{e}\n\n{traceback.format_exc()}")
                once_ = False
            failed.append(data["fed_name"])
    if total == 0:
        return await message.edit(
            f"You Don't have any feds connected!\nSee help {Config.CMD_TRIGGER}addf, for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"<b>Success!</b> Fbanned in {total} feds."
        if len(r_update) != 0:
            for i in r_update:
                status += f"\n• {i}"
    msg_ = (
        fban_arg[3].format(reported, u_link)
        + f"\n**ID:** <code>{u_id}</code>\n**Reason:** {reason}\n**Status:** {status}\n"
    )
    if sudo_:
        msg_ += f"**By:** {message.from_user.mention}"
    del_ = 3 if "-d" in flags_ or Config.F_DEL else -1
    await message.edit(msg_, del_in=del_, dis_preview=True)
    await venom.send_message(
        int(Config.FBAN_LOG_CHANNEL), msg_, dis_preview=True
    )

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'unfban',
        'flags': None,
        'usage': "Unfban user",
        'syntax': '{tr}unfban [username|reply to user|user ID]',
        'sudo': False
    }
)


@venom.trigger('unfban')
async def unfban_(_, message: MyMessage):
    """ Unbans a user from connected Feds. """
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>Un-FBanned {}</b>"]
    await message.edit(fban_arg[0])
    input_ = message.input_str
    if message.reply_to_message:
        reason = input_
        user = message.replied.from_user.id
    else:
        if not input_:
            return await message.edit("`Provide user to unfban...`", del_in=5)
        try:
            split_ = input_.split(" ", 1)
            user = split_[0]
            reason = split_[1]
        except IndexError:
            user = input_
            reason = "not specified, maybe they solved it out"
    proof_channel = Config.FBAN_LOG_CHANNEL if Config.FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
    error_msg = "Provide a User ID or reply to a User"
    if user is None:
        return await message.edit(error_msg, del_in=5)
    try:
        user_ = await venom.get_users(user)
    except (PeerIdInvalid, IndexError, UsernameInvalid):
        return await message.edit(error_msg, del_in=5)
    user = user_.id
    reason = reason or "Not specified"
    failed = []
    total = 0
    await message.edit(fban_arg[1])
    once_ = True
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["_id"])
        try:
            user = f"<a href='tg://user?id={user}'>{user}</a>" if isinstance(user, int) else user
            send_ = await venom.send_message(chat_id, f"/unfban {user} {reason}")
            response = await send_.wait(filters=(filters.user([609517172, 2059887769]) & ~filters.service))
            resp = response.text
            if (
                ("New un-FedBan" not in resp)
                and ("I'll give" not in resp)
                and ("Un-FedBan" not in resp)
            ):
                failed.append(f"{data['fed_name']}  \n__ID__: `{data['_id']}`")
        except BaseException as e:
            if once_:
                await CHANNEL.log(str(e))
                once_ = False
            failed.append(data["fed_name"])
    if total == 0:
        return await message.edit(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )
    await message.edit(fban_arg[2])
    if len(failed) != 0:
        status = f"Failed to un-fban in `{len(failed)}/{total}` feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Un-Fbanned in `{total}` feds."
    msg_ = (
        fban_arg[3].format(user_.mention)
        + f"\n<b>ID:</b> <code>{user}</code>\n<b>Reason:</b> {reason}\n**Status:** {status}"
    )
    await message.edit(msg_)
    await venom.send_message(int(proof_channel), msg_)

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'listf',
        'flags': {
            '-id': 'show fed group id in list',
        },
        'usage': "fed chat list",
        'syntax': '{tr}listf',
        'sudo': True
    }
)


@venom.trigger('listf')
async def fban_lst_(_, message: MyMessage):
    """List all connected Feds."""
    out = ""
    total = 0
    async for data in FED_LIST.find():
        total += 1
        chat_id = data["_id"]
        id_ = f"'<code>{chat_id}</code>' - " if "-id" in message.flags else ""
        out += f"• Fed: {id_}<b>{data['fed_name']}</b>\n"
    await message.edit_or_send_as_file(
        f"**Connected federations: [{total}]**\n\n" + out
        if out
        else "**You haven't connected to any federations yet!**",
        caption="Connected Fed List",
    )

##################################################################################


@venom.trigger('fedmig')
async def fed_migrate(_, message: MyMessage):
    """ migrate fedlist from USERGE-X to VenomX """
    await message.edit("`Migrating federation list...`")
    new_feds = []
    success_ = False
    del_in = 5
    async for one in FED_LIST.find():
        if "chat_type" in one.keys():
            chat_id = one.get("chat_id")
            fed_name = one.get("fed_name")
            new_feds.append({'_id': chat_id, 'fed_name': fed_name})
    for one in new_feds:
        await FED_LIST.insert_one(one)
        success_ = True
        del_in = -1
    await message.edit(
        f"`Migration successful...`\n**Feds migrated:** {len(new_feds)}"
        if success_
        else "`Nothing to migrate...`",
        del_in=del_in
    )
