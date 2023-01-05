# help.py

from pyrogram.enums import ParseMode

from venom import venom, Config, MyMessage, manager
from venom.helpers import plugin_name

dot_ = Config.BULLET_DOT

TRIG = Config.CMD_TRIGGER
S_TRIG = Config.SUDO_TRIGGER

help_ = Config.HELP[plugin_name(__name__)] = {'type': 'help', 'commands': []}

########################################################################################################################

help_['commands'].append(
    {
        'command': 'help',
        'flags': None,
        'usage': 'see command details',
        'syntax': '{tr}help [command name]',
        'sudo': True
    }
)


@venom.trigger('help')
async def cmd_help(_, message: MyMessage):
    """ see command details """
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
    TRIGG = TRIG if message.from_user.id == Config.OWNER_ID else S_TRIG
    await message.edit(out_.replace("{tr}", TRIGG), parse_mode=ParseMode.MARKDOWN, dis_preview=True)


########################################################################################################################


help_['commands'].append(
    {
        'command': 's',
        'flags': None,
        'usage': 'search command or plugin',
        'syntax': '{tr}s [partial command or plugin name]',
        'sudo': True
    }
)


@venom.trigger('s')
async def search_help(_, message: MyMessage):
    """ search command or plugin """
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
