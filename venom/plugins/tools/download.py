# download.py
# ported from USERGE-X fork UX-jutsu
import asyncio
import math
import os
from typing import Union, Tuple
from urllib.parse import unquote_plus
from datetime import datetime

from pySmartDL import SmartDL

from venom import venom, MyMessage, plugin_name, Config
from venom.helpers import human_bytes, progress
from venom.helpers.exceptions import ProcessCancelled

_help = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}


########################################################################################################################

_help['commands'].append(
    {
        'command': 'download',
        'flags': None,
        'usage': 'download media from url or from tg directly',
        'syntax': '{tr}download [reply to tg media] | [url as input]',
        'sudo': False
    }
)


@venom.trigger('download')
async def download_er(_, message: MyMessage):
    """ download media from url or from tg directly """
    replied = message.replied
    if replied and replied.media:
        resource = replied
    elif message.input_str:
        resource = message.input_str
    else:
        return await message.edit("`Reply to media or give input...`", del_in=5)
    download_location, time_took = await handler_download(message, resource)
    await message.edit(f"`Downloaded successfully...`\n<b>Downloaded to:</b> `{download_location}`\n<b>Time took:</b> {time_took}")


async def handler_download(message: MyMessage, resource: Union[MyMessage, str]) -> Tuple[str, int]:
    """ download handler """
    if isinstance(resource, MyMessage):
        return await tg_download(message, resource)
    return await url_download(message, resource)


async def tg_download(message: MyMessage, to_download: MyMessage) -> Tuple[str, int]:
    """ tg media downloader """
    await message.edit("`Downloading from telegram...`")
    start = datetime.now()
    custom_file_name = Config.DOWN_PATH
    if message.filtered_input:
        custom_file_name = os.path.join(custom_file_name, message.filtered_input.strip())
    dl_loc = await venom.download_media(
        message=to_download,
        file_name=custom_file_name,
        progress=progress,
        progress_args=(message, "Trying to download...")
    )
    # dl_loc = await to_download.download(custom_file_name)
    if message.process_is_cancealled:
        raise ProcessCancelled
    if not isinstance(dl_loc, str):
        raise TypeError("File corrupted!")
    # dl_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dl_loc))
    return custom_file_name, (datetime.now() - start).seconds


async def url_download(message: MyMessage, url: str) -> Tuple[str, int]:
    """ url downloader """
    await message.edit("`Downloading from link...`")
    start = datetime.now()
    custom_file_name = unquote_plus(os.path.basename(url))
    if "|" in url:
        url, c_file_name = url.split("|", maxsplit=1)
        url = url.strip()
        if c_file_name:
            custom_file_name = c_file_name.strip()
    dl_loc = os.path.join(Config.DOWN_PATH, custom_file_name)
    downloader = SmartDL(url, dl_loc, progress_bar=False)
    downloader.start(blocking=False)
    count = 0
    while not downloader.isFinished():
        if message.process_is_cancelled:
            downloader.stop()
            raise ProcessCancelled
        total_length = downloader.filesize or 0
        downloaded = downloader.get_dl_size()
        percent = downloader.get_progress() * 100
        speed = downloader.get_speed(human=True)
        estimated_total_time = downloader.get_eta(human=True)
        progress_str = (
            "__{}__\n" +
            "```[{}{}]```\n" +
            "**Progress** : `{}%`\n" +
            "**URL** : `{}`\n" +
            "**FILENAME** : `{}`\n" +
            "**Completed** : `{}`\n" +
            "**Total** : `{}`\n" +
            "**Speed** : `{}`\n" +
            "**ETA** : `{}`"
        )
        progress_str = progress_str.format(
            "Trying to download",
            "".join(
                Config.FINISHED_PROGRESS_STR
                for _ in range(math.floor(percent/5))
            ),
            "".join(
                Config.UNFINISHED_PROGRESS_STR
                for _ in range(20 - math.floor(percent/5))
            ),
            round(percent, 2),
            url,
            custom_file_name,
            human_bytes(downloaded),
            human_bytes(total_length),
            speed,
            estimated_total_time
        )
        count += 1
        if count >= Config.EDIT_SLEEP_TIMEOUT:
            count = 0
            await message.try_to_edit(progress_str, dis_preview=True)
        await asyncio.sleep(1)
    return dl_loc, (datetime.now() - start).seconds
