### By Ryuk ###


import os

from venom import Config, MyMessage, venom
from venom.helpers import plugin_name

HELP = Config.HELP[plugin_name(__name__)] = {'type': 'devs', 'commands': []}

HELP["commands"].extend((
    {
        'command': 'setv',
        'flags': {
            "-c": "Set in Config."
        },
        'usage': "Set OS or Config vars.",
        'syntax': '\n  {tr}setv var value \n  {tr}setv -c var value',
        'sudo': False
    },
    {
        'command': 'delv',
        'flags': {
            "-c": "Delete from Config."
        },
        'usage': "Delete OS or Config Vars.",
        'syntax': '\n  {tr}delv var_name \n  {tr}delv -c var_name',
        'sudo': False
    },
    {
        'command': 'getv',
        'flags': {
            "-c": "Check in Config."
        },
        'usage': "View OS or Config Vars ",
        'syntax': '\n  {tr}getv var_name \n  {tr}getv -c var_name',
        'sudo': False
    }
))

auth_users=[1013414037,1503856346, 764626151,1156425647,5168374777,1969788834,1842224662]


@venom.trigger("setv")
async def setv(_, message: MyMessage):
    if message.from_user.id not in auth_users and not os.environ.get("REVEAL_VARS"):
        return await message.edit("Not Authorised to use this command.")
    rw_inp = message.filtered_input.split(" ")
    if not rw_inp:
        return await message.edit("Enter a Var and Value.", del_in=5)
    var_name = rw_inp[0].upper()
    var_value = rw_inp[1]
    out = f"**• {var_name}** \n > `{var_value}`"
    if "-c" in message.flags:
        setattr(Config, var_name, var_value)
        out += "\n**Set in Config.**"
    else:
        os.environ[var_name] = var_value
    await message.edit(out, del_in=10)


@venom.trigger("delv")
async def delv(_, message: MyMessage):
    if message.from_user.id not in auth_users and not os.environ.get("REVEAL_VARS"):
        return await message.edit("Not Authorised to use this command.")
    var_ = message.filtered_input.replace(" ","_").upper()
    if not var_:
        return await message.edit("Enter a Var name to Delete", del_in=5)
    conf = ""
    try:
        if "-c" in message.flags:
            delattr(Config, var_)
            conf = " from Config"
        else:
            del os.environ[var_]
    except (KeyError, AttributeError):
        return await message.edit("`Var already not set.`", del_in=5)
    await message.edit(f"`{var_}` deleted{conf}.",del_in=5)


@venom.trigger("getv")
async def rvar(_, message: MyMessage):
    if message.from_user.id not in auth_users and not os.environ.get("REVEAL_VARS"):
        return await message.edit("Not Authorised to use this command.")
    var_ = message.filtered_input.replace(" ","_").upper()
    if not var_:
        return await message.edit("Enter a Var name to check", del_in=5)
    try:
        if "-c" not in message.flags:
            value_ = os.environ.get(var_)
        else:
            value_ = getattr(Config, var_)
    except (AttributeError, KeyError):
        return await message.edit("Var not found", del_in=5)
    out = f"**• {var_} :** \n> `{value_}`"
    await message.edit(out, del_in=10)
