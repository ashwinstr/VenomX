# reply.py

from venom import Config, venom
from venom.core.types.message import MyMessage
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}

###############################################################################################################################################################

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
    " reply to any message "
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
