""" shell runner """
import asyncio

from venom import Config, MyMessage, venom
from venom.helpers import run_shell_cmd

Config().help_formatter(
    name=__name__,
    command="sh",
    flags=None,
    usage="Run shell commands",
    syntax="{tr}sh [code]",
    sudo=False
)


@venom.trigger("sh")
async def shell_cmd(_, message: MyMessage):
    """ Run shell commands """
    cmd = message.input_str.strip()
    await message.edit("<code>Executing...</code>")
    try:
        proc_stdout = await asyncio.create_task(run_shell_cmd(cmd), name=message.unique_id)
    except asyncio.CancelledError:
        return await message.edit("<code>Cancelled...</code>")
    output = f"<pre language=shell>~${cmd}\n\n{proc_stdout}</pre>"
    await message.edit_or_send_as_file(output, file_name="sh.txt", dis_preview=True)