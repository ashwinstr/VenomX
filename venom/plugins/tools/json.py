# json.py

from venom import venom, Config, MyMessage
from venom.helpers import plugin_name

HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}

###########################################################################################################################################

HELP['commands'].append(
    {
        'command': 'json',
        'flags': None,
        'about': 'message entity in json format',
        'sudo': True
    }
)

@venom.trigger('json')
async def j_son(_, message: MyMessage):
    " message entity in json format "
    msg = message.msg.reply_to_message if message.replied else message.msg
    await message.edit_or_send_as_file(f"```{str(msg)}```", file_name="json.txt", caption=f"JSON of message.")