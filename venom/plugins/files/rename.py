import asyncio
import os
import shutil
import time

from ub_core.utils.downloader import Download, DownloadedFile
from ub_core.utils.helpers import progress

from venom import MyMessage, venom
from venom.plugins.files.download import telegram_download
from venom.plugins.files.upload import FILE_TYPE_MAP


@venom.trigger(cmd="rename")
async def rename(_, message: MyMessage):
    """
    CMD: RENAME
    INFO: Upload Files with custom name
    FLAGS: -s for spoiler
    USAGE:
        .rename [ url | reply to message ] file_name.ext
    """
    input = message.filtered_input
    response = await message.reply("Checking input...")
    if not message.replied or not message.replied.media or not message.filtered_input:
        await response.edit(
            "Invalid input...\nReply to a message containing media or give a link and a filename with cmd."
        )
        return
    dl_path = os.path.join("downloads", str(time.time()))
    await response.edit("Input verified....Starting Download...")
    if message.replied:
        download_coro = telegram_download(
            message=message.replied,
            path=dl_path,
            file_name=input,
            response=response,
        )
    else:
        url, file_name = input.split(maxsplit=1)
        dl_obj: Download = await Download.setup(
            url=url, path=dl_path, message_to_edit=response, custom_file_name=file_name
        )
        download_coro = dl_obj.download()
    try:
        downloaded_file: DownloadedFile = await download_coro
        media: dict = await FILE_TYPE_MAP[downloaded_file.type](
            downloaded_file, has_spoiler="-s" in message.flags
        )
        progress_args = (
            response,
            "Uploading...",
            downloaded_file.name,
            downloaded_file.full_path,
        )
        await media["method"](
            chat_id=message.chat.id,
            progress=progress,
            progress_args=progress_args,
            **media["kwargs"]
        )
        shutil.rmtree(dl_path, ignore_errors=True)
        await response.delete()
    except asyncio.exceptions.CancelledError:
        await response.edit("Cancelled....")
    except TimeoutError:
        await response.edit("Download Timeout...")
    except Exception as e:
        await response.edit(str(e))
