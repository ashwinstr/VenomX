# help.py

from typing import List

from pyrogram import filters
from pyrogram.types import InlineQuery
from pyrogram.enums import ParseMode

from venom import venom, Config, MyMessage, manager
from venom.helpers import plugin_name, post_tg, VenomDecorators


help_ = Config.HELP[plugin_name(__name__)] = {'type': 'help', 'commands': []}
dot_ = Config.BULLET_DOT

TRIG = Config.CMD_TRIGGER


############################################################################################################################################

help_['commands'].append(
    {
        'command': 'help',
        'flags': None,
        'about': 'check help',
        'syntax': '{tr}help',
        'sudo': True
    }
)

@venom.trigger('help')
async def help_me(_, message: MyMessage):
    " check help "
    help__ = f"""
Hello there, **{message.from_user.first_name}**, this is VenomX help.

**To check list of plugins...**
`{TRIG}plugins`

**To check inside a plugin...**
`{TRIG}plugin [plugin name]`

**To check about a command...**
`{TRIG}cmd [command name]`

**To search for plugin or command...**
`{TRIG}s [query]`

For anything else, ask for help in @UX_xplugin_support.
**THANK YOU.**
    """

    await message.edit(help__, parse_mode=ParseMode.MARKDOWN)


############################################################################################################################################

help_['commands'].append(
    {
        'command': 'plugins',
        'flags': {
            '-tg': 'show plugins in telegraph'
        },
        'about': 'check plugin list',
        'syntax': '{tr}plugins',
        'sudo': True
    }
)


@venom.trigger('plugins')
async def plugin_s(_, message: MyMessage):
    " check plugin list "
    out_ = "<b>Available plugins:</b> [<b>{}</b>]<br><br>"
    total_ = 0
    for plug in manager.plugin_names():
        out_ += f"{dot_} <b>{plug}</b><br>"
        total_ += 1
    if "-tg" not in message.flags:
        out_ = out_.replace("<br>", "\n")
        return await message.edit(out_.format(total_))
    link_ = post_tg("VenomX plugins list.", out_.format(total_))
    return await message.edit(f"<b>VenomX</b> plugins list is <b>[HERE]({link_})</b>.", dis_preview=True)


##########################################################################################################################################################


help_['commands'].append(
    {
        'command': 'plugin',
        'flags': None,
        'about': 'check command list in plugin',
        'syntax': '{tr}plugin [plugin name]',
        'sudo': True
    }
)

@venom.trigger('plugin')
async def plug_in(_, message: MyMessage):
    " check command list in plugin "
    input_ = message.input_str
    if not input_:
        return await message.edit("`Input not found...`")
    if input_ not in manager.plugin_names():
        return await message.edit(f"The input `{input_}` is <b>not</b> a valid plugin name.")
    out_ = "Available commands in <b>{}</b>: [<b>{}</b>]<br><br>"
    total_ = 0
    cmd_list = Config.HELP[input_]['commands'] if input_ in Config.HELP.keys() else None
    if cmd_list:
        for cmd in cmd_list:
            out_ += f"{dot_} <b>{cmd['command']}</b><br>  <b>About:</b> {cmd['about'] if 'about' in cmd.keys() else 'Not documented.'}<br><br>"
            total_ += 1
        out_ = out_.format(input_, total_)
    else:
        out_ = "`Not documented.`"
    out_ = out_.replace("<br>", "\n")
    await message.edit(out_)


##############################################################################################################################################################


help_['commands'].append(
    {
        'command': 'cmd',
        'flags': None,
        'about': 'see command details',
        'syntax': '{tr}cmd [command name]',
        'sudo': True
    }
)

@venom.trigger('cmd')
async def com_mand(_, message: MyMessage):
    " see command details "
    input_ = message.input_str
    if not input_:
        return await message.edit("`Input not found...`")
    if input_ not in manager.cmd_names():
        return await message.edit(f"Input `{input_}` is <b>not</b> a valid command.")
    out_ = f"--Details on command **{input_}**--:\n\n"
    parent_ = manager.cmd_parent_plugin(input_)
    help_ = Config.HELP[parent_]['commands'] if parent_ in Config.HELP.keys() else None
    if help_ is not None:
        my_cmd = None
        for one in help_:
            if one['command'] == input_:
                my_cmd = one
                break
    else:
        my_cmd = None
    if my_cmd:
        gh_link = manager.gh_link(input_)
        sytx = my_cmd['syntax'] if 'syntax' in my_cmd.keys() else 'Not documented.'
        flags_ = my_cmd['flags'] if 'flags' in my_cmd.keys() and my_cmd['flags'] is not None else None
        _flags = "None\n"
        if flags_:
            _flags = "\n"
            for k, v in flags_.items():
                _flags += f"    `{str(k)}` : __{str(v)}__\n"
        out_ += (
            f"{dot_} **Name:** `{input_}`\n"
            f"{dot_} **Flags:** {_flags}"
            f"{dot_} **Syntax:** `{sytx}`\n"
            f"{dot_} **Sudo access:** {my_cmd['sudo'] if 'sudo' in my_cmd.keys() else '`Not documented.`'}\n\n"

            f"**Location:** `{manager.plugin_loc(parent_)}`\n"
            f"**GitHub link:** **[LINK]({gh_link})**"
        )
    else:
        out_ = "`Not documented.`"
    await message.edit(out_.replace("{tr}", TRIG), parse_mode=ParseMode.MARKDOWN, dis_preview=True)


#####################################################################################################################################################


help_['commands'].append(
    {
        'command': 's',
        'flags': None,
        'about': 'search command or plugin',
        'syntax': '{tr}s [partial command or plugin name]',
        'sudo': True
    }
)

@venom.trigger('s')
async def search_help(_, message: MyMessage):
    " search command or plugin "
    out_ = "<u>Searching <b>plugins</b> with '<b>{}</b>'</u>: [<b>{}</b>]\n\n"
    input_ = message.input_str
    plug_ = ""
    ptotal = 0
    for one in manager.plugin_names():
        if input_ in one:
            plug_ += f"{dot_} `{one}`\n"
            ptotal += 1
    if not ptotal:
        plug_ = "`No match found.`\n"
    out_ = out_.format(input_, ptotal) + plug_

    out_ += "\n<u>Searching <b>commands</b> with '<b>{}</b>'</u>: [<b>{}</b>]\n\n"
    cmd_ = ""
    ctotal = 0
    for one in manager.cmd_names():
        if input_ in one:
            cmd_ += f"{dot_} `{one}`\n"
            ctotal += 1
    if not ctotal:
        cmd_ = "`No match found.`"
    out_ = out_.format(input_, ptotal) + cmd_
    await message.edit(out_)