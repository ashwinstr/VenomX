# sudo.py

import asyncio
import bisect

from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied

from venom import venom, Config, Collection, MyMessage


help_ = Config.HELP['sudo'] = {'type': 'tools', 'commands': []}


async def _init() -> None:
    toggle = await Collection.TOGGLES.find_one({'_id': "SUDO_TOGGLE"})
    if toggle:
        if toggle['switch'] == True:
            Config.SUDO = True
        else:
            Config.SUDO = False
    async for data in Collection.TRUSTED_SUDO_USERS.find():
        Config.TRUSTED_SUDO_USERS.append(data['_id'])
    async for data in Collection.SUDO_USERS.find():
        Config.SUDO_USERS.append(data['_id'])
    async for cmds in Collection.SUDO_CMD_LIST.find():
        Config.SUDO_CMD_LIST = cmds['commands']

##########################################################################################################################################


help_['commands'].append(
    {
        'command': 'sudo',
        'flags': {
            '-c': 'check status'
        },
        'about': 'toggle for sudo access'
    }
)

@venom.trigger('sudo')
async def sudo_toggle(_, message: MyMessage):
    " sudo toggles "
    if "-c" in message.flags:
        if Config.SUDO:
            trigger_ = "ON"
        else:
            trigger_ = "OFF"
        return await message.edit(f"The **SUDO** trigger is currently **{trigger_}**.")
    if Config.SUDO:
        Config.SUDO = False
        switch_ = "OFF"
    else:
        Config.SUDO = True
        switch_= "ON"
    Collection.TOGGLES.update_one(
        {'_id': 'SUDO_TOGGLE'}, {'$set': {'switch': Config.SUDO}}, upsert=True
    )
    await message.edit(f"The **SUDO** switch is now **{switch_}**.")


##########################################################################################################################################


help_['commands'].append(
    {
        'command': 'addsudo',
        'flags': {
            '-t': 'add to trusted sudo'
        },
        'about': 'add user to sudo'
    }
)

@venom.trigger('addsudo')
async def add_sudo(_, message: MyMessage):
    " add sudo users "
    replied = message.replied
    user_ = message.filtered_input if not replied else replied.from_user.id
    if not user_:
        return await message.edit("`Input not found...`")
    try:
        user_ = await venom.get_users(user_)
    except (PeerIdInvalid, UsernameNotOccupied):
        return await message.edit(f"The provided user `{user_}` is **not valid**.")
    tsudo = False
    sudo = False
    if user_.id in Config.TRUSTED_SUDO_USERS:
        tsudo = True
    elif user_.id in Config.SUDO_USERS:
        sudo = True
    if "-t" in message.flags:
        if tsudo:
            return await message.edit(f"User `{user_.id}` **already** in Trusted sudo user list.")
        elif sudo:
            Config.SUDO_USERS.remove(user_.id)
            await Collection.SUDO_USERS.delete_one({'_id': user_.id})
            action_ = "moved to"
        else:
            action_ = "added to"
        Config.TRUSTED_SUDO_USERS.append(user_.id)
        await Collection.TRUSTED_SUDO_USERS.insert_one({'_id': user_.id, 'username': user_.username})
        return await message.edit(f"User `{user_.id}` {action_} **Trusted sudo user** list.")
    if tsudo:
        Config.TRUSTED_SUDO_USERS.remove(user_.id)
        await Collection.TRUSTED_SUDO_USERS.delete_one({'_id': user_.id})
        action_ = "moved to"
    elif sudo:
        return await message.edit(f"User `{user_.id}` **already** in Sudo user list.")
    else:
        action_ = "added to"
    Config.SUDO_USERS.append(user_.id)
    await Collection.SUDO_USERS.insert_one({'_id': user_.id, 'username': user_.username})
    await message.edit(f"User `{user_.id}` {action_} **Sudo user** list.")


##########################################################################################################################################


help_['commands'].append(
    {
        'command': 'delsudo',
        'flags': {
            '-all': 'remove all sudo users'
        },
        'about': 'remove sudo user from lists'
    }
)

@venom.trigger('delsudo')
async def del_sudo(_, message: MyMessage):
    " del user from sudo "
    if "-all" in message.flags:
        await asyncio.gather(
            Collection.TRUSTED_SUDO_USERS.drop(),
            Collection.SUDO_USERS.drop()
        )
        Config.TRUSTED_SUDO_USERS.clear()
        Config.SUDO_USERS.clear()
        return await message.edit("**All users removed from Sudo lists.**")
    replied = message.replied
    user_ = replied.from_user.id if replied else message.filtered_input
    if not user_:
        return await message.edit("`Input not found...`")
    try:
        user_ = await venom.get_users(user_)
    except PeerIdInvalid:
        return await message.edit(f"The provided user `{user_}` is **not valid**.")
    if user_.id in Config.SUDO_USERS:
        await Collection.SUDO_USERS.delete_one({'_id': user_.id})
        Config.SUDO_USERS.remove(user_.id)
        from_ = "Sudo user list"
    elif user_.id in Config.TRUSTED_SUDO_USERS:
        await Collection.TRUSTED_SUDO_USERS.delete_one({'_id': user_.id})
        Config.TRUSTED_SUDO_USERS.remove(user_.id)
        from_ = "Trusted sudo user list"
    else:
        return await message.edit(f"User `{user_.id}` **doesn't exist** in sudo user lists.")
    await message.edit(f"The user `{user_.id}` is **removed** from {from_}.")


##########################################################################################################################################


help_['commands'].append(
    {
        'command': 'vsudo',
        'flags': None,
        'about': 'view sudo user lists'
    }
)

@venom.trigger('vsudo')
async def view_sudo(_, message: MyMessage):
    " view sudo user lists "
    list_ = "**Trusted sudo user list:** [**{}**]\n\n"
    t_total = 0
    dot_ = Config.BULLET_DOT
    async for one in Collection.TRUSTED_SUDO_USERS.find():
        list_ += f"{dot_} `{one['_id']}` - **@{one['username']}**\n"
        t_total += 1
    if t_total == 0:
        list_ += "`EMPTY LIST!`\n"
    list_ += "\n**Normal sudo user list:** [**{}**]\n\n"
    n_total = 0
    async for one in Collection.SUDO_USERS.find():
        list_ += f"{dot_} `{one['_id']}` - **@{one['username']}**\n"
        n_total += 1
    if n_total == 0:
        list_ += "`EMPTY LIST!`"
    await message.edit(list_.format(t_total, n_total))


##########################################################################################################################################


dangerous_cmds = [
    'term',
    'eval',
    'sudo',
    'addsudo',
    'delsudo',
]

help_['commands'].append(
    {
        'command': 'addscmd',
        'flags': {
            '-all': 'add all available commands to sudolist'
        },
        'about': 'add commands to sudolist for sudo users'
    }
)

@venom.trigger('addscmd')
async def add_s_cmd(_, message: MyMessage):
    " add commands to sudolist for sudo users "
    if "-all" in message.flags:
        total_ = 0
        Config.SUDO_CMD_LIST.clear()
        for cmd in Config.CMD_LIST:
            if cmd in dangerous_cmds:
                continue
            Config.SUDO_CMD_LIST.append(cmd)
            total_ += 1
        return await asyncio.gather(
            Collection.SUDO_CMD_LIST.update_one(
                {'_id': 'SUDO_CMD_LIST'}, {'$set': {'commands': Config.SUDO_CMD_LIST}}, upsert=True
            ),
            message.edit(f"`Added all {total_} commands to sudo command list.`")
        )
    input_ = message.filtered_input
    if not input_:
        out_ = "`Input not found...`"
    elif input_ not in Config.CMD_LIST:
        out_ = f"`Input {input_} is not a valid command...`"
    elif input_ in dangerous_cmds:
        out_ = f"`Command {input_} is a dangerous command, hence can't be added to sudo command list."
    elif input_ in Config.SUDO_CMD_LIST:
        out_ = f"`Command {input_} is already in the sudo command list.`"
    else:
        bisect.insort(Config.SUDO_CMD_LIST, input_)
        out_ = f"Command `{input_}` **added** to sudo command list."
        await Collection.SUDO_CMD_LIST.update_one(
            {'_id': 'SUDO_CMD_LIST'}, {'$set': {'commands': Config.SUDO_CMD_LIST}}, upsert=True
        )
    await message.edit(out_)


##########################################################################################################################


help_['commands'].append(
    {
        'command': 'delscmd',
        'flags': {
            '-all': 'delete all commands from sudolist'
        },
        'about': 'delete commands from the sudolist for sudo users'
    }
)

@venom.trigger('delscmd')
async def del_s_cmd(_, message: MyMessage):
    " delete commands from the sudolist for sudo users "
    if "-all" in message.flags:
        confirm_ = await message.ask("Are you sure? Reply '`yes.`' for yes...")
        if confirm_.text.lower() == 'yes.':
            Config.SUDO_CMD_LIST.clear()
            await Collection.SUDO_CMD_LIST.drop()
            out_ = "`Cleared sudo command list.`"
        else:
            out_ = "`Process cancelled.`"
        return await message.edit(out_)
    input_ = message.filtered_input
    if not input_:
        out_ = "`Input not found...`"
    elif input_ not in Config.CMD_LIST:
        out_ = f"`Input {input_} is not a valid command.`"
    elif input_ not in Config.SUDO_CMD_LIST:
        out_ = f"`Command {input_} doesn't exist in sudo commands list.`"
    else:
        Config.SUDO_CMD_LIST.remove(input_)
        await Collection.SUDO_CMD_LIST.update_one(
            {'_id': 'SUDO_CMD_LIST'}, {'$set': {'commands': Config.SUDO_CMD_LIST}}, upsert=True
        )
        out_ = f"Command `{input_}` **removed** from sudo command list."
    await message.edit(out_)


############################################################################################################################################################


help_['commands'].append(
    {
        'command': 'vscmd',
        'flags': None,
        'about': 'see all commands available to sudos'
    }
)

@venom.trigger('vscmd')
async def view_s_cmd(_, message: MyMessage):
    " see all commands available to sudos "
    out_ = "**Commands available to Sudo users:** [**{}**]"
    list_ = "`    `".join(Config.SUDO_CMD_LIST)
    total_ = len(Config.SUDO_CMD_LIST)
    if not total_:
        list_ = "`EMPTY!`"
    await message.edit(f"{out_.format(total_)}\n\n`{list_}`")