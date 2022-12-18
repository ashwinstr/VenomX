from venom import MyMessage, venom, Config 
from pyrogram.errors import UsernameInvalid
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}
HELP_['commands'].extend([
    {
        'command': 'join',
        'flags': None,
        'usage': 'join private / public chat using link or @',
        'syntax': (
            '{tr}join chat_link or @'
        ),
        'sudo': True
    },
    {
        'command': 'click',
        'flags': None,
        'usage': 'Click a button in replied message.',
        'syntax': (
            '{tr}click Yes'
            '__Note__: **Is case sensitive.**'
            'Defaults to 1st button if no input is provided.'
        ),
        'sudo': True
    }
])


@venom.trigger("join")
async def join_chat(_,message: MyMessage):
    reply = message.reply_to_message
    link = reply.text or message.input_str
    if not link:
        return await message.edit(
            "Bruh, can't Join without a Link...", del_in=3
        )
    try:
        await venom.join_chat(link)
    except UsernameInvalid:
        link = link.split("/")[-1]
        await venom.join_chat(link)
    except Exception as e:
        if str(e).startswith("Telegram says: [400 Bad Request] - [400 INVITE_REQUEST_SENT]"):
            return await message.reply("Join Request Sent.")
    await message.reply("Joined")



@venom.trigger("click")
async def clck(_,message: MyMessage):
    button_name = message.input_str
    button = message.reply_to_message
    if not button:
        return await message.edit("Reply to a button -_-", del_in=5)
    try:
        if button_name:
            await button.click(button_name)
        else:
            await button.click(0)
    except ValueError:
        return await message.reply("Button doesn't exists")
    except TimeoutError:
        return
