# regex test plugin

import re

from pyrogram.enums import ParseMode

from venom import venom, MyMessage, Config, plugin_name

help_ = Config.HELP[plugin_name(__name__)] = {'type': 'devs', 'commands': []}

########################################################################################################################

help_['commands'].append(
    {
        'command': 'regex',
        'flags': {
            '-m': 'match',
            '-s': 'search',
            '-f': 'find all'
        },
        'usage': 'for testing regex',
        'syntax': '{tr}regex [flag]\n[pattern]\n[text in next line]',
        'sudo': True
    }
)


@venom.trigger("regex")
async def regex_101(_, message: MyMessage):
    """ regex test plugin """
    flags_ = message.flags
    if not flags_:
        return await message.edit(
            f"**Flag needed...**\nSee `{Config.CMD_TRIGGER}help regex` to know more.",
            parse_mode=ParseMode.MARKDOWN,
            del_in=5
        )
    if len(flags_) > 1:
        return await message.edit("`Can't have more than one flags...`", del_in=5)
    input_ = message.input_str
    err_msg = "**{}** not found...\nSee `{}help regex`"
    if not input_:
        return await message.edit(
            err_msg.format("Pattern", Config.CMD_TRIGGER),
            parse_mode=ParseMode.MARKDOWN,
            del_in=5
        )
    split_input = input_.split("\n")
    string_ = "\n".join(split_input[2:]) if len(split_input) >= 3 else None
    if not string_:
        return await message.edit(
            err_msg.format("String", Config.CMD_TRIGGER),
            parse_mode=ParseMode.MARKDOWN,
            del_in=5
        )
    pattern_ = split_input[1]
    if '-m' in flags_:
        method_ = re.match
        method_name = "Match"
    elif '-s' in flags_:
        method_ = re.search
        method_name = "Search"
    else:
        method_ = re.findall
        method_name = "Find all"
    try:
        regex_ = method_(pattern_.strip(), string_.strip(), re.MULTILINE)
    except Exception as e:
        return await message.edit(f"**Error:** {e}")
    format_ = f"**Method:** `{method_name}`\n**Pattern:** `{pattern_}`\n**Input:** `{string_}`"
    if not regex_:
        return await message.edit(f"{format_}\n\n`No match found...`")
    if hasattr(regex_, "groups") and len(regex_.groups()) != 0:
        regex_ = regex_.groups()
    out_ = f"""
{format_}

**Match:** ```
{regex_}```
    """
    await message.edit(out_, parse_mode=ParseMode.MARKDOWN)
