""" base_64.py """

import base64

from venom import venom, Config, plugin_name, MyMessage

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'b64',
        'flags': {
            '-d': 'decode',
            '-s': 'secret'
        },
        'usage': 'decode/encode with base64',
        'syntax': '{tr}b64 [optional flag] text',
        'sudo': True
    }
)


@venom.trigger('b64')
async def base_64_(_, message: MyMessage):
    """ decode/encode with base64 """
    flags = message.flags
    text = message.filtered_input
    func = base64.b64encode
    task = "Encoding"
    if "-d" in flags:
        func = base64.b64decode
        task = "Decoding"
    edit_out = f"**{task}** `{text}`..." if "-s" not in flags else "`Encoding...`"
    await message.edit(edit_out)
    new_text = func(text)
    out = f"**Input:** `{text}`\n" if "-s" not in flags else ""
    out += f"**{task[:-3]}ed:** {new_text}"
    await message.edit(out)
