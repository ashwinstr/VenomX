# help.py

from venom import venom, Config, MyMessage
from venom.helpers import plugin_name, post_tg


help_ = Config.HELP[plugin_name(__name__)] = {'type': 'help', 'commands': []}
dot_ = Config.BULLET_DOT


############################################################################################################################################

help_['commands'].append(
    {
        'command': 'help',
        'flags': {
            '-tg': 'show help in telegraph'
        },
        'about': 'check help of all commands'
    }
)


@venom.trigger('help')
async def help_me(_, message: MyMessage):
#    " check help for all commands "
#    query_ = message.filtered_input
#    if not query_:
        out_ = "<b>Available commands:</b> [<b>{}</b>]<br><br>"
        total_ = 0
        for plugins in Config.HELP.keys():
            out_ += f"{dot_} <b>{plugins}</b><br>"
            commands = Config.HELP[plugins]['commands']
            for cmd in commands:
                total_ += 1
                sudo = f"<i>{cmd['sudo']}</i>" if 'sudo' in cmd.keys() else "<i>N.A.</i>"
                line_ = f"    {dot_} <code>{cmd['command']}</code><br>"
                line_ += f"      <b>About:</b> <i>{cmd['about']}</i>\n"
                line_ += f"      <b>Sudo access</b>: {sudo}<br>"
                out_ += f"{line_}<br>"
            out_ += "<br>"
        if "-tg" not in message.flags:
            out_ = out_.replace("<br>", "\n")
            return await message.edit(out_.format(total_))
        link_ = post_tg("VenomX commands help.", out_.format(total_))
        return await message.edit(f"<b>VenomX</b> plugins help is <b>[HERE]({link_})</b>.", dis_preview=True)