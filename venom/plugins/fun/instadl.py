# instadl.py
# made by Ryuk

import asyncio
import os
import shutil
from subprocess import call
from time import time

import requests
import yt_dlp
from pyrogram.errors import MediaEmpty, WebpageCurlFailed
from pyrogram.types import User
from wget import download as wget_dl

from venom import Config, MyMessage, venom
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'fun', 'commands': []}
CHANNEL = venom.getCLogger(__name__)
selenium_error = ""

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'viddl',
        'flags': None,
        'usage': 'social media video downloader',
        'syntax': '{tr}viddl [link]',
        'sudo': True
    }
)


@venom.trigger(r'viddl')
async def insta_dl(_, message: MyMessage):
    """ social media video downloader """
    link_ = message.input_str
    if not link_:
        return await message.edit("`Provide a link to download from...`")
    chat_id = message.chat.id
    del_link = True
    caption = "Shared by: "
    if message.sender_chat:
        caption += message.author_signature
    else:
        caption += (await venom.get_users(message.from_user.id)).first_name
    msg = await message.reply("`Trying to download...`")
    start_time = time()
    dl_path = f"downloads/{str(start_time)}"
    try:
        _opts = {
            "outtmpl": f"{dl_path}/video.mp4",
            "format": "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
            "prefer_ffmpeg": True,
            "postprocessors": [{"key": "FFmpegMetadata"}, {"key": "EmbedThumbnail"}],
        }
        x = yt_dlp.YoutubeDL(_opts).download(link_)
        video_path = f"{dl_path}/video.mp4"
        thumb_path = f"{dl_path}/i.jpg"
        call(
            f'''ffmpeg -ss 0.1 -i "{video_path}" -vframes 1 "{thumb_path}"''',
            shell=True,
        )
        await venom.send_video(chat_id, video_path, thumb=thumb_path, caption=caption)
        if os.path.exists(str(dl_path)):
            shutil.rmtree(dl_path)
    except Exception as e:
        if str(e).startswith("ERROR: [Instagram]"):
            await msg.edit("Couldn't download video,\n`Trying alternate method....`")
            i_dl = await asyncio.to_thread(downloader(link_))
            if i_dl == "not_found":
                await msg.edit("Video download failed.\nLink not supported or private.")
            else:
                try:
                    await message.reply_video(i_dl, caption=caption)
                except (MediaEmpty, WebpageCurlFailed):
                    x = wget_dl(i_dl, "x.mp4")
                    await message.reply_video(x, caption=caption)
                    if os.path.exists(x):
                        os.remove(x)
                except Exception as e:
                    await CHANNEL.log(str(e))
        else:
            await CHANNEL.log(str(e))
            if selenium_error:
                await CHANNEL.log(f"Selenium error found:\n\n{selenium_error}")
            await message.reply("**Link not supported or private.**")
            del_link = False
    await msg.delete()
    if del_link:
        await message.delete()

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'reddl',
        'flags': None,
        'usage': 'reddit downloader',
        'syntax': '{tr}reddl [link]',
        'sudo': True
    }
)


@venom.trigger('reddl')
async def reddit_dl(_, message: MyMessage):
    """ reddit downloader """
    ext = None
    del_link = True
    m = message.input_str.split()
    msg = await message.reply("`Trying to download...`")
    for link_ in m:
        if link_.startswith("https://www.reddit.com"):
            link = link_.split("/?")[0] + ".json?limit=1"
            headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_7 rv:5.0; en-US) AppleWebKit/533.31.5 ("
                              "KHTML, like Gecko) Version/4.0 Safari/533.31.5 "
            }
            req = requests.get(link, headers=headers)
            try:
                json_ = req.json()
                data = json_[0]['data']['children'][0]['data']
                check_ = data['secure_media']
                title_ = data['title']
                subr = data['subreddit_name_prefixed']
                caption = f"__{subr}:__\n**{title_}**\n\nShared by : "
                if message.sender_chat:
                    caption += message.author_signature
                else:
                    caption += (await venom.get_users(message.from_user.id)).first_name
                if isinstance(check_, dict):
                    time_ = str(time())
                    dl_path = f"downloads/{time_}"
                    os.mkdir(dl_path)
                    v = f"{dl_path}/v.mp4"
                    t = f"{dl_path}/i.png"
                    vid_url = data['secure_media']['reddit_video']['hls_url']
                    call(
                        f'ffmpeg -hide_banner -loglevel error -i "{vid_url.strip()}" -c copy {v}',
                        shell=True,
                    )
                    call(f"""ffmpeg -ss 0.1 -i '{v}' -vframes 1 '{t}'""", shell=True)
                    await message.reply_video(v, caption=caption, thumb=t)
                    if os.path.exists(str(dl_path)):
                        shutil.rmtree(dl_path)
                else:
                    media_: str = data['url_overridden_by_dest']
                    try:
                        if media_.strip().endswith(".gif"):
                            ext = ".gif"
                            await message.reply_animation(media_, caption=caption)
                        elif media_.strip().endswith((".jpg", ".jpeg", ".png", ".webp")):
                            ext = ".png"
                            await message.reply_photo(media_, caption=caption)
                    except (MediaEmpty, WebpageCurlFailed):
                        wget_dl(media_, f"i{ext}")
                        if ext == ".gif":
                            await venom.send_animation(
                                message.chat.id,
                                "i.gif",
                                unsave=True,
                                caption=caption
                            )
                        else:
                            await message.reply_photo("i.png", caption=caption)
                        if os.path.exists(f"i{ext}"):
                            os.remove(f"i{ext}")
            except Exception as e:
                del_link = False
                await CHANNEL.log(str(e))
                await msg.edit("Link doesn't contain any media or is restricted\nTip: Make sure you are sending "
                               "original post url and not an embedded post.")
    if del_link:
        await message.delete()
        await msg.delete()


def downloader(url) -> str:
    global selenium_error
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import WebDriverException, InvalidSessionIdException

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

    try:
        driver.get(f"https://en.savefrom.net/258/#url={url}")
        link = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#sf_result .info-box a"))
        )
        rlink = link.get_attribute("href")
    except BaseException as e:
        rlink = "not found"
        selenium_error = str(e)
    try:
        driver.close()
    except InvalidSessionIdException:
        pass
    except Exception as e:
        selenium_error = str(e)
    return rlink


def full_name(user: User) -> str:
    try:
        f_name = " ".join([user.first_name, user.last_name or ""])
    except BaseException:
        raise
    return f_name
