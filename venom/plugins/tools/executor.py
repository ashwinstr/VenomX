# executor.py

import logging
import sys
import io
import keyword
import traceback

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from venom import venom, Config
from venom.helpers import post_tg


filters_ = (
    filters.command("eval", prefixes=Config.CMD_TRIGGER)
    & filters.user(Config.OWNER_ID)
)

@venom.on_message(filters_, group=1)
@venom.on_edited_message(filters_, group=2)
async def evaluate(_, message: Message):
    " evaluate your code "
    if " " or "\n" in message.text:
        cmd = (message.text).split(maxsplit=1)[-1]
    else:
        return await message.edit("`Input not found...`")
    await message.edit("`Executing eval...`")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    ret_val, stdout, stderr, exc = None, None, None, None

    async def aexec(code):
        head = "async def __aexec(venom, message):\n "
        if "\n" in code:
            rest_code = "\n ".join(iter(code.split("\n")))
        elif (
            any(
                True
                for k_ in keyword.kwlist
                if k_ not in ("True", "False", "None") and code.startswith(f"{k_} ")
            )
            or "=" in code
        ):
            rest_code = f"\n {code}"
        else:
            rest_code = f"\n return {code}"
        exec(head + rest_code)  # nosec pylint: disable=W0122
        return await locals()["__aexec"](venom, message)

    try:
        ret_val = await aexec(cmd)
    except Exception:  # pylint: disable=broad-except
        exc = traceback.format_exc().strip()
    stdout = redirected_output.getvalue().strip()
    stderr = redirected_error.getvalue().strip()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or ret_val
    output = f"**>** ```{cmd}```\n\n"
    if evaluation is not None:
        output += f"**>>** ```{evaluation}```"
    if output and len(output) <= 4096:
        await message.edit(
            text=output, parse_mode=ParseMode.MARKDOWN
        )
    elif output and len(output > 4096):
        link_ = post_tg(f"Eval output with Venomx.", output)
        await message.edit(f"Eval output is **[HERE]({link_})**.")
    else:
        await message.delete()