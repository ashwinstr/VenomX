### By Ryuk ###


import os
import glob
import shutil
import traceback
from time import time

import yt_dlp
from wget import download

from venom import MyMessage, venom, plugin_name, Config, logging, test_print

LOGGER = logging.getLogger(__name__)
CHANNEL = venom.getCLogger(__name__)
HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'song',
        'flags': {
            '-m': 'to get mp3'
        },
        'usage': 'Download songs',
        'syntax': '{tr}song [song name]',
        'sudo': True
    }
)


@venom.trigger('song')
async def song_dl(_, message: MyMessage):
    reply_query = None
    audio_path = None
    thumb_path = None
    artist = None
    thumb = None
    reply = message.reply_to_message
    if reply:
        for link in reply.text.split():
            if link.startswith(
                ("https://www.youtube", "https://youtube", "https://music.youtube")
            ):
                reply_query = link
                break
    query = reply_query or message.filtered_input
    if not query:
        return await message.edit("`Give a song name or link to download.`", del_in=5)
    await message.edit("`Searching...`")
    start_time = time()
    dl_path = f"downloads/{start_time}/"
    query_or_search = query if query.startswith("http") else f"ytsearch:{query}"
    if "-m" in message.flags:
        aformat = "mp3"
    else:
        aformat = "opus"
    yt_opts = {
        "logger": LOGGER,
        "outtmpl": dl_path + "%(title)s.%(ext)s",
        "format": "bestaudio",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": aformat},
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"}
        ],
    }
    with yt_dlp.YoutubeDL(yt_opts) as ytdl:
        try:
            yt_info = ytdl.extract_info(query_or_search)
            if not query_or_search.startswith("http"):
                yt_info = yt_info["entries"][0]
            thumb = yt_info["thumbnails"]
            duration = yt_info["formats"][0]["fragments"][0]["duration"]
            artist = yt_info["channel"]
        except Exception as e:
            test_print(e)
            await CHANNEL.log(str(traceback.format_exc()))
    if thumb:
        try:
            nthumb = thumb[-11]["url"]
        except IndexError:
            nthumb = thumb[-1]["url"]
        thumb_path = download(nthumb, dl_path)
    for i in glob.glob(dl_path+'*'):
        if i.endswith((".opus",".mp3")):
            audio_path = i
    if audio_path is not None:
        await message.edit("`Uploading...`")
        await message.reply_audio(
            audio=audio_path,
            duration=int(duration),
            performer=str(artist),
            thumb=thumb_path,
        )
        await message.delete()
    else:
        return await message.edit("Not found")
    if os.path.exists(str(dl_path)):
        shutil.rmtree(dl_path)