# instadl.py
# made by Ryuk

import os
import shutil
from subprocess import call
from time import time

import yt_dlp
from pyrogram import filters
from pyrogram.errors import MediaEmpty, WebpageCurlFailed
from pyrogram.types import User

from venom import venom, Config, MyMessage
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'fun', 'commands': []}
CHANNEL = venom.getCLogger(__name__)

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'insta',
        'flags': None,
        'usage': 'insta reels downloader',
        'syntax': '{tr}insta [link]',
        'sudo': True
    }
)


@venom.trigger('insta ')
async def insta_dl(_, message: MyMessage):
    """ insta reels downloader """


@venom.on_message(
    filters.regex(r"https://twitter.com/*")
    | filters.regex(r"^https://youtube.com/shorts/*")
    | filters.regex(r"^https://vm.tiktok.com/*")
    | filters.regex(r"^\.dl"),
    group=3
)
async def video_dl(_, message: MyMessage):
    chat_id = message.chat.id
    del_link = True
    if message.from_user.id == Config.OWNER_ID and message.text.startswith(".dl"):
        caption = "Shared by : "
        if message.sender_chat:
            caption += message.author_signature
        else:
            caption += (await venom.get_users(message.from_user.id)).first_name
        msg = await message.reply("`Trying to download...`")
        raw_message = message.text.split()
        for link in raw_message:
            if link.startswith("http"):
                start_time = time()
                dl_path = f"downloads/{str(start_time)}"
                try:
                    _opts = {
                        "outtmpl": f"{dl_path}/video.mp4",
                        "format": "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
                        "prefer_ffmpeg": True,
                        "postprocessors": [{"key": "FFmpegMetadata"}, {"key": "EmbedThumbnail"}],
                    }
                    x = yt_dlp.YoutubeDL(_opts).download(link)
                    video_path = f"{dl_path}/video.mp4"
                    thumb_path = f"{dl_path}/i.jpg"
                    call(
                        f'''ffmpeg -ss 0.1 -i "{video_path}" -vframes 1 "{thumb_path}"''',
                        shell=True,
                    )
                    await venom.send_video(chat_id, video=video_path, thumb=thumb_path, caption=caption)
                    if os.path.exists(str(dl_path)):
                        shutil.rmtree(dl_path)
                except Exception as e:
                    if str(e).startswith("ERROR: [Instagram]"):
                        await msg.edit(
                            "Couldn't download video,\n`trying alternate method....`"
                        )
                        i_dl = downloader(link)
                        if i_dl == "not found":
                            await message.reply(
                                "Video download failed.\nLink not supported or private."
                            )
                        else:
                            try:
                                await message.reply_video(i_dl, caption=caption)
                            except (MediaEmpty, WebpageCurlFailed):
                                from wget import download

                                x = download(i_dl, "x.mp4")
                                await message.reply_video(x, caption=caption)
                                if os.path.exists(x):
                                    os.remove(x)
                    else:
                        await CHANNEL.log(str(e))
                        await message.reply("**Link not supported or private.** 🥲")
                        del_link = False
                    continue
        await msg.delete()
        if del_link or message.from_user.id == 1503856346:
            await message.delete()


def downloader(url):
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximised")
        chrome_options.binary_location = Config.GOOGLE_CHROME_BIN
        chrome_options.add_argument("ignore-certificate-errors")
        chrome_options.add_argument("test-type")
        chrome_options.add_argument("headless")
        chrome_options.add_argument("no-sandbox")
        chrome_options.add_argument("disable-dev-shm-usage")
        chrome_options.add_argument("no-sandbox")
        chrome_options.add_argument("disable-gpu")

        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.get(f"https://en.savefrom.net/258/#url={url}")
        link = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#sf_result .info-box a"))
        )
        rlink = link.get_attribute("href")
        driver.close()
    except BaseException:
        rlink = "not found"
    return rlink


def full_name(user: User):
    try:
        f_name = " ".join([user.first_name, user.last_name or ""])
    except BaseException:
        raise
    return f_name
