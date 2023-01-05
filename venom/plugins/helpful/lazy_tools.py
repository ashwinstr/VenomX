# by Ryuk and Kakashi

from pyrogram.errors import UsernameInvalid, PeerIdInvalid

from venom import venom, MyMessage, Config, plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}
CHANNEL = venom.getCLogger(__name__)

HELP_['commands'].extend([
    {
        'command': 'joinc',
        'flags': None,
        'usage': 'join private / public chat using link or @username',
        'syntax': (
            '{tr}join chat_link or @username'
        ),
        'sudo': True
    },
    {
        'command': 'click',
        'flags': None,
        'usage': ('Click a button in replied message.\n'
                  '**Note:** Is case sensitive.\n'
                  'Defaults to 1st button if no input is provided.'),
        'syntax': '{tr}click Yes',
        'sudo': True
    }
])

################################################### joinc ##############################################################


@venom.trigger("joinc")
async def join_chat(_, message: MyMessage):
    reply = message.reply_to_message
    link = reply.text if reply else message.input_str
    if not link:
        return await message.edit(
            "Bruh, can't Join without a Link...", del_in=3
        )
    try:
        await venom.join_chat(link)
    except UsernameInvalid:
        link = link.split("/")[-1]
        await venom.join_chat(link)
    except BaseException as e:
        if str(e).startswith("Telegram says: [400 Bad Request] - [400 INVITE_REQUEST_SENT]"):
            return await message.reply("`Join Request Sent.`")
        else:
            raise e
    await message.reply("`Joined.`")

#################################################### click #############################################################


@venom.trigger("click")
async def click_it(_, message: MyMessage):
    button_name = message.input_str
    button = message.reply_to_message
    if not button:
        return await message.edit("`Reply to a button...`", del_in=5)
    try:
        if button_name:
            if button_name.isdigit():
                button_name = int(button_name)
            await button.click(button_name)
        else:
            await button.click(0)
    except ValueError:
        await message.edit("`Button doesn't exists...`")
    except AttributeError:
        await message.edit("`Reply to a message with button...`")
    except TimeoutError:
        return

###################################################### reply ###########################################################

HELP_['commands'].append(
    {
        'command': 'reply',
        'flags': {
            '-c': 'change client'
        },
        'usage': 'reply to any message',
        'syntax': '{tr}reply text',
        'sudo': False
    }
)


@venom.trigger('reply')
async def reply_(_, message: MyMessage):
    """ reply to any message """
    input_ = message.input_str
    flags = message.flags
    if not input_:
        return
    reply_ = message.replied
    reply_to = reply_.id if reply_ else None
    if '-c' not in flags:
        await venom.both.send_message(message.chat.id, input_, reply_to_message_id=reply_to)
    else:
        await venom.both.bot.send_message(message.chat.id, input_, reply_to_message_id=reply_to)

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'invite',
        'flags': None,
        'usage': 'Invite user to group.',
        'syntax': '{tr}invite [username|id]',
        'sudo': True
    }
)


@venom.trigger('invite')
async def invite_user(_, message: MyMessage):
    """ invite user to group """
    user_ = message.input_str
    if not user_:
        return await message.edit("`Provide user to invite...`", del_in=5)
    try:
        user_entity = await venom.get_users(user_)
    except (UsernameInvalid, PeerIdInvalid):
        return await message.edit("`Invalid user...`", del_in=5)
    try:
        await venom.add_chat_members(message.chat.id, user_entity.id)
    except BaseException as e:
        await CHANNEL.log(str(e))
        return await message.edit("`Couldn't invite the user...`", del_in=5)
    await message.edit("`Invited successfully.`")
