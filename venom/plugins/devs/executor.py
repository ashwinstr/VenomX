# executor.py
# taken from USERGE-X

import asyncio
import io
import keyword
import sys
import traceback

from pyrogram import filters

try:
    from os import geteuid
except ImportError:

    def geteuid() -> int:
        return 1


from getpass import getuser

from pyrogram.enums import ParseMode

from venom import venom, Config, MyMessage, SecureConfig, Collection
from venom.helpers import post_tg, plugin_name
from . import init_func


help_ = Config.HELP[plugin_name(__name__)] = {"type": "tools", "commands": []}


async def _init() -> None:
    found = await Collection.TOGGLES.find_one({"_id": "DEVELOPER_MODE"})
    if found:
        Config.DEVELOPER_MODE = SecureConfig().DEVELOPER_MODE = found["switch"]

    else:
        await Collection.TOGGLES.insert_one({"_id": "DEVELOPER_MODE", "switch": False})


########################################################################################################################


help_["commands"].append(
    {
        "command": "eval",
        "flags": {
            "-tg": "telegraph",
            "-m": "markdown",
        },
        "about": "evaluate your code",
        "sudo": False,
    }
)


@venom.trigger("eval")
async def evaluate(_, message: MyMessage):
    """evaluate your code"""
    cmd = await init_func(message)
    mono_ = True if "-m" not in message.flags else False
    tele_ = True if "-tg" in message.flags else False
    if not cmd:
        return
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
        proc_ = aexec(cmd)
        task_ = Config._TASKS[message.unique_id] = asyncio.Task(proc_)
        ret_val = await task_
        Config._TASKS.pop(message.unique_id)
    except Exception:  # pylint: disable=broad-except
        exc = traceback.format_exc().strip()
    except asyncio.CancelledError:
        exc = "Eval cancelled..."
    stdout = redirected_output.getvalue().strip()
    stderr = redirected_error.getvalue().strip()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or ret_val
    output = f"**>** `{cmd}`\n\n"
    if evaluation is not None:
        if mono_:
            try:
                output += f"**>>** `{evaluation}`"
            except RecursionError:
                output += "**>>** `None`"
            parse_ = ParseMode.MARKDOWN
        else:
            output += f"**>>** {evaluation}"
            parse_ = ParseMode.DEFAULT
    else:
        parse_ = ParseMode.MARKDOWN
    if output:
        if tele_:
            link_ = post_tg(f"Eval output with VenomX.", output)
            return await message.edit(f"Eval output is **[HERE]({link_})**.")
        await message.edit_or_send_as_file(
            output, file_name="eval.txt", caption=cmd, parse_mode=parse_
        )
    else:
        await message.delete()


########################################################################################################################

help_["commands"].append(
    {"command": "term", "flags": None, "about": "run commands in shell", "sudo": False}
)


@venom.trigger("term")
async def term_(_, message: MyMessage):
    """run commands in shell (terminal with live update)"""
    cmd = await init_func(message)
    if cmd is None:
        return
    cmd = message.input_str
    await message.edit("`Executing terminal ...`")
    try:
        t_obj = await Term.execute(cmd)  # type: Term
    except Exception as t_e:  # pylint: disable=broad-except
        await message.edit(str(t_e))
        return
    curruser = getuser()
    uid = geteuid()
    output = f"{curruser}:~# {cmd}\n" if uid == 0 else f"{curruser}:~$ {cmd}\n"
    count = 0
    while not t_obj.finished:
        count += 1
        if message.process_is_cancelled:
            t_obj.cancel()
            return await message.reply("`Process cancelled!`")
        await asyncio.sleep(0.5)
        if count >= Config.EDIT_SLEEP_TIMEOUT * 2:
            count = 0
            out_data = f"<pre>{output}{t_obj.read_line}</pre>"
            await message.try_to_edit(out_data, parse_mode=ParseMode.HTML)
    out_data = f"<pre>{output}{t_obj.get_output}</pre>"
    await message.edit_or_send_as_file(
        out_data, parse_mode=ParseMode.HTML, file_name="term.txt", caption=cmd
    )


########################################################################################################################

help_["commands"].append(
    {
        "command": "dev_mode",
        "flags": {"-c": "check status"},
        "usage": "Enable/disable developer mode",
        "syntax": "{tr}dev_mode true/false",
        "sudo": False,
    }
)


@venom.trigger("dev_mode")
async def developer_mode(_, message: MyMessage):
    """toggle developer mode"""
    if message.from_user.id != Config.OWNER_ID:
        return await message.edit(
            "`Only the owner of the bot can use this command.`", del_in=5
        )
    flags_ = message.flags
    if "-c" in flags_:
        return await message.edit(
            "Developer mode is " + "**ON**" if Config.DEVELOPER_MODE else "**OFF**"
        )
    input_ = message.filtered_input
    warn_ = await message.edit(
        "**Are you sure...? You will be held responsible for future consequences in case your data is stolen.**\n"
        "Reply `Yes, I'm fully aware of the consequences.` to continue."
    )
    try:
        resp_ = await warn_.wait(filters=filters.user(Config.OWNER_ID))
    except asyncio.TimeoutError:
        return await message.reply("`Response not found... Process aborted.`", del_in=5)
    if resp_.text != "Yes, I'm fully aware of the consequences.":
        return await message.edit(
            f"Your response **{resp_.text}** does not match.\n`Aborting process...`",
            del_in=5,
        )
    if input_.lower() == "true":
        Config.DEVELOPER_MODE = SecureConfig().DEVELOPER_MODE = True
    elif input_.lower() == "false":
        Config.DEVELOPER_MODE = SecureConfig().DEVELOPER_MODE = False
    else:
        return await message.edit("`Invalid input...`", del_in=5)
    await message.edit(
        "Developer mode changed to " + "**ON**" if Config.DEVELOPER_MODE else "**OFF**"
    )
    await Collection.TOGGLES.update_one(
        {"_id": "DEVELOPER_MODE"},
        {"$set": {"switch": Config.DEVELOPER_MODE}},
        upsert=True,
    )


########################################################################################################################


class Term:
    """live update term class"""

    def __init__(self, process: asyncio.subprocess.Process) -> None:
        self._process = process
        self._stdout = b""
        self._stderr = b""
        self._stdout_line = b""
        self._stderr_line = b""
        self._finished = False

    def cancel(self) -> None:
        self._process.kill()

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def read_line(self) -> str:
        return (self._stdout_line + self._stderr_line).decode("utf-8").strip()

    @property
    def get_output(self) -> str:
        return (self._stdout + self._stderr).decode("utf-8").strip()

    async def _read_stdout(self) -> None:
        while True:
            line = await self._process.stdout.readline()
            if line:
                self._stdout_line = line
                self._stdout += line
            else:
                break

    async def _read_stderr(self) -> None:
        while True:
            line = await self._process.stderr.readline()
            if line:
                self._stderr_line = line
                self._stderr += line
            else:
                break

    async def worker(self) -> None:
        await asyncio.wait(
            [asyncio.Task(self._read_stdout()), asyncio.Task(self._read_stderr())]
        )
        await self._process.wait()
        self._finished = True

    @classmethod
    async def execute(cls, cmd: str) -> "Term":
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        t_obj = cls(process)
        asyncio.get_event_loop().create_task(t_obj.worker())
        return t_obj
