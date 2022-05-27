# cancel.py
# took from USERGE-X

from venom import venom, MyMessage, Config
from venom.helpers import plugin_name


HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}


#################################################################################################################################################


HELP['commands'].append(
    {
        'command': 'cancel',
        'flags': None,
        'about': 'cancel running message process',
        'syntax': '{tr}cancel [reply to message]',
        'sudo': False
    }
)

@venom.trigger('cancel')
async def cancel_(_, message: MyMessage):
    " cancel running message process "
    replied = message.replied
    if not replied:
        return await message.edit("`Reply to message to cancel process...`")
    replied.cancel_process()
    await message.edit("`Process cancelled of replied message.`")
    