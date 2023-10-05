# tools imported from USERGE-X repo

import asyncio
import math
import shlex
import time
from typing import Tuple, Dict, Optional

from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery

import venom
from venom import helpers

_TASKS: Dict[str, Tuple[float, float]] = {}


def human_bytes(size: float) -> str:
    """ humanize size """
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def progress(
        current: int,
        total: int,
        message: "venom.MyMessage",
        ud_type: str,
        file_name: str = "",
        c_q: CallbackQuery = None,
        delay: int = venom.config.Config.EDIT_SLEEP_TIMEOUT,
) -> None:
    """ progress function """
    if message.process_is_cancelled:
        await message.client.stop_transmission()
    task_id = f"{message.chat.id}.{message.id}"
    if current == total:
        if task_id not in _TASKS:
            return
        del _TASKS[task_id]
        try:
            if c_q:
                await c_q.edit_message_text("`Finalizing process ...`")
            else:
                await message.try_to_edit("`Finalizing process ...`")
        except FloodWait as f_e:
            await asyncio.sleep(f_e.value)
        return
    now = time.time()
    if task_id not in _TASKS:
        _TASKS[task_id] = (now, now)
    start, last = _TASKS[task_id]
    elapsed_time = now - start
    if (now - last) >= delay:
        _TASKS[task_id] = (start, now)
        percentage = current * 100 / total
        speed = current / elapsed_time
        time_to_completion = helpers.time_format(int((total - current) / speed))
        progress_str = (
                "__{}__ : `{}`\n"
                + "```[{}{}]```\n"
                + "**Progress** : `{}%`\n"
                + "**Completed** : `{}`\n"
                + "**Total** : `{}`\n"
                + "**Speed** : `{}/s`\n"
                + "**ETA** : `{}`"
        )
        progress_str = progress_str.format(
            ud_type,
            file_name,
            "".join(
                (
                    venom.Config.FINISHED_PROGRESS_STR
                    for i in range(math.floor(percentage / 5))
                )
            ),
            "".join(
                (
                    venom.Config.UNFINISHED_PROGRESS_STR
                    for i in range(20 - math.floor(percentage / 5))
                )
            ),
            round(percentage, 2),
            human_bytes(current),
            human_bytes(total),
            human_bytes(speed),
            time_to_completion if time_to_completion else "0 s",
        )
        try:
            if c_q:
                await c_q.edit_message_text(progress_str)
            else:
                await message.try_to_edit(progress_str)
        except FloodWait as f_e:
            await asyncio.sleep(f_e.value)


def get_file_id(message: 'venom.MyMessage') -> Optional[str]:
    """ get file id from message """
    if message is None:
        return
    file_ = (
        message.audio
        or message.animation
        or message.photo
        or message.sticker
        or message.voice
        or message.video_note
        or message.video
        or message.document
    )
    return file_.file_id if file_ else None
