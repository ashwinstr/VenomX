# directories.py

import os
import shutil
from os.path import exists
from pathlib import Path

from venom import venom, Config, MyMessage
from venom.helpers import plugin_name, human_bytes

HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}

########################################################################################################################

HELP['commands'].append(
    {
        'command': 'ls',
        'flags': {
            '-d': 'downloads'
        },
        'about': 'check directories',
        'syntax': '{tr}ls [directory path]',
        'sudo': True
    }
)


@venom.trigger('ls')
async def direct_ories(_, message: MyMessage):
    """ check directories """
    path_ = "downloads" if '-d' in message.flags else message.input_str or "."
    if not exists(path_):
        return await message.edit(f"Path `{path_}` does not exist.", del_in=3)
    path = Path(path_)
    out = f"<b>PATH:</b> `{path}`\n\n"
    if path.is_dir():
        folders = ""
        files = ""
        for one_path in sorted(path.iterdir()):
            if one_path.is_file():
                if str(one_path).endswith((".mp3", ".flac", ".wav", ".m4a")):
                    files += "🎵"
                elif str(one_path).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
                    files += "📹"
                elif str(one_path).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp")):
                    files += "🖼"
                else:
                    files += "📄"
                size = os.stat(str(one_path)).st_size
                files += f" `{one_path.name}` <i>({human_bytes(size)})\n"
            else:
                folders += f"📁 <code>{one_path.name}</code>\n"
        out += (folders + files) or "<code>empty path!</code>"
    else:
        size = os.stat(str(path)).st_size
        out += f"📄 <code>{path.name}</code> <i>({human_bytes(size)})</i>\n"
    await message.edit_or_send_as_file(out)

########################################################################################################################

# HELP['commands'].append(
#     {
#         'command': 'downloads',
#         'flags': {
#             '-c': 'clear'
#         },
#         'usage': 'Check downloads folder',
#         'syntax': '{tr}downloads',
#         'sudo': True
#     }
# )
#
#
# @venom.trigger('downloads')
# async def down_loads(_, message: MyMessage):
#     """ Check downloads folder """
#     flags_ = message.flags
#     if "-c" in flags_:
#         shutil.rmtree(Config.DOWN_PATH)
#         return await message.edit("`Cleared downloads folder...`", del_in=5)
#     await message.edit
