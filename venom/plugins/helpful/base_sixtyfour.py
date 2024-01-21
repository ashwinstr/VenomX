""" base_sixtyfour.py """

import base64

from venom import venom, Config, MyMessage

# HELP_ = Config.help_formatter(__name__)

########################################################################################################################

# HELP_['commands'].append(
#     {
#         'command': 'b64',
#         'flags': {
#             '-d': 'decode',
#             '-s': 'secret'
#         },
#         'usage': 'decode/encode with base64',
#         'syntax': '{tr}b64 [optional flag] text',
#         'sudo': True
#     }
# )

Config().help_formatter(
    name=__name__,
    command='b64',
    flags={
        '-d': 'decode',
        '-s': 'secret'
    },
    usage='decode/encode with base64',
    syntax='{tr}b64 [optional flags] text',
    sudo=True
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
    edit_out = f"**{task}** `{text}`..." if "-s" not in flags else f"`{task}...`"
    await message.edit(edit_out)
    new_text = func(bytes(text.encode('utf-8')))
    out = f"**Input:** `{text}`\n" if "-s" not in flags else ""
    out += f"**{task[:-3]}ed:** `{new_text.decode()}`"
    await message.edit(out)
