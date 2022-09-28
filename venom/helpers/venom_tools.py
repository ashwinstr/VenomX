# venom tools

import json
import time
import re
import os
from typing import Union
from telegraph import Telegraph, upload_file
from pastypy import Paste

from pymediainfo import MediaInfo

from os.path import isfile, relpath
from typing import Union, List
from glob import glob

from pyrogram.raw.types import (
    InputPeerUserFromMessage,
    InputReportReasonPornography,
    InputReportReasonSpam,
)
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.errors import UserIdInvalid

from venom import logging, Config, MyMessage, Collection
from venom.core.types.message import MyMessage

_LOG = logging.getLogger(__name__)

tele_ = Telegraph()


def plugin_name(name: str) -> str:
    " return plugin name from plugin path "
    split_ = name.split(".")
    plugin_name_ = split_[-1]
    return plugin_name_


def get_import_paths(root: str, path: str) -> Union[str, List[str]]:
    " get import paths "
    seperator = "\\" if "\\" in root else "/"
    if isfile(path):
        return '.'.join(relpath(path, root)).split(seperator)[:-3]
    all_paths = glob(root + path.rstrip(seperator) + f"{seperator}*.py", recursive=True)
    return sorted(
        [
            ".".join(relpath(f, root).split(seperator))[:-3]
            for f in all_paths
            if not f.endswith("__init__.py")
        ]
    )


def post_tg(title: str, content: str) -> str:
    " post to telegraph "
    auth_name = tele_.create_account(short_name="VenomX")
    resp = tele_.create_page(
        title=title,
        author_name=auth_name,
        author_url="https://t.me/UX_xplugin_support",
        html_content=content,
    )
    link_ = resp["url"]
    return link_


async def post_tg_media(message: MyMessage) -> str:
    " upload media to telegraph "
    media = message.replied
    if (not media.photo
        and not media.animation
        and (not media.video
            or not (media.video.file_name).endswith(".mp4", ".mkv"))
            and (not media.document
                and (not media.document.file_name).endswith(".png", ".jpeg", ".jpg", ".gif", ".mkv", ".mp4"))):
        return await message.edit("`File not supported.`")
    await message.edit("`Downloading...`")
    down_ = await media.download(Config.DOWN_PATH)
    await message.edit("`Uploading to telegraph...`")
    try:
        up_ = upload_file(down_)
    except Exception as t_e:
        return await message.edit(f"<b>ERROR:</b>\n {str(t_e)}")
    os.remove(down_)
    return f"https://telegra.ph{up_[0]}"

def get_owner() -> dict:
    file_ = open("venom/xcache/user.txt", "r")
    data = file_.read()
    if not data:
        _LOG.info("NO USERNAME FOUND!!!")
    user = json.loads(str(data))
    return user

def time_format(time: float) -> str:
    " time formatter "
    days_ = time / 60 / 60 / 24
    hour_ = (days_ - int(days_)) * 24
    min_ = (hour_ - int(hour_)) * 60
    sec_ = (min_ - int(min_)) * 60
    out_ = f"<b>{int(days_)}</b>d," if int(days_) else ""
    out_ += f" <b>{int(hour_)}</b>h," if int(hour_) else ""
    out_ += f" <b>{int(min_)}</b>m," if int(min_) else ""
    out_ += f" <b>{int(sec_)}</b>s"
    return out_.strip()

def time_stamp(time: float) -> str:
    " time stamp "
    hour_ = time / 60 / 60
    min_ = (hour_ - int(hour_)) * 60
    sec_ = (min_ - int(min_)) * 60
    out_ = f"{int(hour_):02}:" if int(hour_) >= 1 else ""
    out_ += f"{int(min_):02}:{int(sec_):02}"
    return out_

def extract_id(mention):
    if str(mention).isdigit():
        raise UserIdInvalid
    elif mention.startswith("@"):
        raise UserIdInvalid
    try:
        men = mention.html
    except:
        raise UserIdInvalid
    filter = re.search(r"\d+", men)
    if filter: 
        return filter.group(0)
    raise UserIdInvalid

def report_user(chat: int, user_id: int, msg: dict, msg_id: int, reason: str):
    if ("nsfw" or "NSFW" or "porn") in reason:
        reason_ = InputReportReasonPornography()
        for_ = "pornographic message"
    else:
        reason_ = InputReportReasonSpam()
        for_ = "spam message"
    peer_ = (
        InputPeerUserFromMessage(
            peer=chat,
            msg_id=msg_id,
            user_id=user_id,
        ),
    )
    ReportPeer(
        peer=peer_,
        reason=reason_,
        message=msg,
    )
    return for_

class Media_Info:
    def data(media: str) -> dict:
        "Get downloaded media's information"
        found = False
        media_info = MediaInfo.parse(media)
        for track in media_info.tracks:
            if track.track_type == "Video":
                found = True
                type_ = track.track_type
                format_ = track.format
                duration_1 = track.duration
                other_duration_ = track.other_duration
                duration_2 = f"{other_duration_[0]} - ({other_duration_[3]})" if other_duration_ else None
                pixel_ratio_ = [track.width, track.height]
                aspect_ratio_1 = track.display_aspect_ratio
                other_aspect_ratio_ = track.other_display_aspect_ratio
                aspect_ratio_2 = other_aspect_ratio_[0] if other_aspect_ratio_ else None
                fps_ = track.frame_rate
                fc_ = track.frame_count
                media_size_1 = track.stream_size
                other_media_size_ = track.other_stream_size
                media_size_2 = [other_media_size_[1], other_media_size_[2], other_media_size_[3], other_media_size_[4]] if other_media_size_ else None

        dict_ = {
            "media_type": type_,
            "format": format_,
            "duration_in_ms": duration_1,
            "duration": duration_2,
            "pixel_sizes": pixel_ratio_,
            "aspect_ratio_in_fraction": aspect_ratio_1,
            "aspect_ratio": aspect_ratio_2,
            "frame_rate": fps_,
            "frame_count": fc_,
            "file_size_in_bytes": media_size_1,
            "file_size": media_size_2
        } if found else None
        return dict_

async def paste_it(msg_content: Union[MyMessage, str]) -> str:
    " paste content to pasty.lus "
    if isinstance(msg_content, MyMessage):
        reply_ = msg_content.replied
        if reply_.document:
            if "text/" not in str(reply_.document.mime_type):
                return False
            await msg_content.edit("`Downloading document...`")
            down_ = await reply_.download()
            with open(down_, "r") as file_:
                content_ = file_.read()
            os.remove(down_)
        elif reply_.text or reply_.caption:
            content_ = reply_.text or reply_.caption
        else:
            return False
    elif isinstance(msg_content, str):
        content_ = msg_content
    paste_ = Paste(content=content_)
    paste_.save()
    return paste_.url

async def restart_msg(msg: MyMessage, text: str = "") -> None:
    try:
        await Collection.RESTART.insert_one(
            {
                '_id':'RESTART',
                'chat_id': msg.chat.id,
                'msg_id': msg.id,
                'start': time.time(),
                'text': text
            }
        )
    except Exception as e:
        await msg.edit(e)