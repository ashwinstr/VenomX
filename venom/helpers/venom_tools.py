# venom tools
import json
import os
import re
import time
from glob import glob
from os.path import isfile, relpath
from typing import Union, List

from pastypy import Paste
from pymediainfo import MediaInfo
from pyrogram.raw.types.input_report_reason_spam import InputReportReasonSpam
from pyrogram.raw.types.input_report_reason_pornography import InputReportReasonPornography
from pyrogram.errors import UserIdInvalid
from pyrogram.raw.functions.messages.report import Report
from telegraph import Telegraph

import venom
from venom import logging, Config, Collection
from .exceptions import VarNotFoundException
from ..core.types import message

_LOG = logging.getLogger(__name__)

tele_ = Telegraph()


def plugin_name(name: str) -> str:
    """ return plugin name from plugin path """
    split_ = name.split(".")
    plugin_name_ = split_[-1]
    return plugin_name_


def get_import_paths(root: str, path: str) -> Union[str, List[str]]:
    """ get import paths """
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
    """ post to telegraph """
    auth_name = tele_.create_account(short_name="VenomX")
    resp = tele_.create_page(
        title=title,
        author_name=auth_name,
        author_url="https://t.me/UX_xplugin_support",
        html_content=content,
    )
    link_ = resp["url"]
    return link_


async def post_tg_media(content: Union['message.MyMessage', str]) -> str:
    """ upload media to telegraph """
    if isinstance(content, message.MyMessage):
        media = content.replied if content.replied else content
        if (not media.photo
                and not media.animation
                and (not media.video
                     or not media.video.file_name.endswith(".mp4"))
                and (not media.document
                     and not media.document.file_name.endswith((".png", ".jpeg", ".jpg", ".gif", ".mp4")))):
            await content.edit("`File not supported.`")
            return ""
        await content.edit("`Downloading...`")
        down_ = await media.download(Config.DOWN_PATH)
        await content.edit("`Uploading to telegraph...`")
        try:
            up_ = Telegraph().upload_file(f=down_)
        except Exception as t_e:
            await content.edit(f"<b>ERROR:</b>\n {str(t_e)}")
            return ""
        os.remove(down_)
    elif isinstance(content, str):
        try:
            up_ = Telegraph().upload_file(content)
        except BaseException as t_e:
            print(t_e)
            return ""
    else:
        return ""
    return f"https://telegra.ph{up_[0]}"


def get_owner() -> dict:
    file_ = open("venom/xcache/user.txt", "r")
    data = file_.read()
    if not data:
        _LOG.info("NO USERNAME FOUND!!!")
    user = json.loads(str(data))
    return user


def time_format(time_: float) -> str:
    """ time formatter """
    days_ = time_ / 60 / 60 / 24
    hour_ = (days_ - int(days_)) * 24
    min_ = (hour_ - int(hour_)) * 60
    sec_ = (min_ - int(min_)) * 60
    out_ = f"<b>{int(days_)}</b>d," if int(days_) else ""
    out_ += f" <b>{int(hour_)}</b>h," if int(hour_) else ""
    out_ += f" <b>{int(min_)}</b>m," if int(min_) else ""
    out_ += f" <b>{int(sec_)}</b>s"
    return out_.strip()


def time_stamp(time_: float) -> str:
    """ time stamp """
    hour_ = time_ / 60 / 60
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
    filter_ = re.search(r"\d+", men)
    if filter_:
        return filter_.group(0)
    raise UserIdInvalid


async def report_user(
        # chat: int,
        user_id: int,
        msg_id: int,
        reason: str
):
    if ("nsfw" or "NSFW" or "porn") in reason:
        reason_ = InputReportReasonPornography()
        for_ = "pornographic message"
    else:
        reason_ = InputReportReasonSpam()
        for_ = "spam message"
    # resolved = await venom.venom.resolve_peer(peer_id=user_id)
    # if not isinstance(resolved, InputUser):
    # return
    # user_ = await venom.venom.invoke(GetUsers(id=[resolved]))
    # if not isinstance(user_, User) or not isinstance(user_.access_hash, int):
    # return
    # input_peer_user = InputPeerUser(user_id=user_id, access_hash=user_.access_hash)
    resolved_chat = await venom.venom.resolve_peer(user_id)
    # chat_ = input_peer_chat.InputPeerChat(chat_id=resolved_chat.channel_id)
    reporting = Report(
        peer=resolved_chat,
        id=[msg_id],
        reason=reason_,
        message=for_
    )
    await venom.venom.invoke(reporting)
    return for_


class Media_Info:

    @staticmethod
    def data(media: str) -> dict | None:
        """ Get downloaded media's information """
        media_info = MediaInfo.parse(media)
        for track in media_info.tracks:
            if track.track_type == "Video":
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
                media_size_2 = [other_media_size_[1], other_media_size_[2], other_media_size_[3],
                                other_media_size_[4]] if other_media_size_ else None
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
                }
                return dict_
        return None


async def paste_it(msg_content: Union['message.MyMessage', str]) -> str:
    """ paste content to pasty.lus """
    if isinstance(msg_content, message.MyMessage):
        reply_ = msg_content.replied if msg_content.replied else msg_content
        if reply_.document:
            try:
                await msg_content.edit("`Downloading document...`")
                down_ = await reply_.download()
                with open(down_, "r", encoding="utf8") as file_:
                    content_ = file_.read()
                os.remove(down_)
            except BaseException as e:
                print(e)
                return "Failed..."
        elif reply_.text or reply_.caption:
            content_ = reply_.text or reply_.caption
        else:
            print("Not document nor message text")
            return "Failed..."
    elif isinstance(msg_content, str):
        content_ = msg_content
    else:
        print("Not message nor string")
        return "Failed..."
    paste_ = Paste(content=content_)
    paste_.save()
    return paste_.url


async def restart_msg(msg: 'message.MyMessage', text: str = "") -> None:
    try:
        await Collection.RESTART.insert_one(
            {
                '_id': 'RESTART',
                'chat_id': msg.chat.id,
                'msg_id': msg.id,
                'start': time.time(),
                'text': text
            }
        )
    except Exception as e:
        await msg.edit(str(e))


def current_time(hour_diff: float = Config.TIME_DIFF) -> dict:
    """ get current time with time difference in hours as input """
    time_sec = time.time()
    diff_in_hour = hour_diff
    diff_in_seconds = diff_in_hour * 60 * 60
    current_time_in_seconds = time_sec + diff_in_seconds
    day_ = current_time_in_seconds / (60 * 60 * 24)
    hour_ = (day_ - int(day_)) * 24
    minutes_ = (hour_ - int(hour_)) * 60
    seconds_ = int((minutes_ - int(minutes_)) * 60)
    minutes_ = int(minutes_)
    hour_ = int(hour_)
    if seconds_ > 59:
        minutes_ += 1
        seconds_ -= 60
    if minutes_ > 59:
        hour_ += 1
        minutes_ -= 60
    if hour_ > 23:
        hour_ -= 24
    if hour_ < 12:
        stamp_ = "AM"
    else:
        stamp_ = "PM"
    minutes_ = f"{minutes_:02}"
    hour_ = f"{hour_:02}"
    seconds_ = f"{seconds_:02}"
    time_dict = {
        "H": hour_,
        "M": minutes_,
        "S": seconds_,
        "STAMP": stamp_
    }
    return time_dict


class CurrentTime:

    def __init__(self):
        self._current_time = current_time()

    @property
    def h(self) -> str:
        """ hours """
        return self._current_time['H']

    @property
    def m(self) -> str:
        """ minutes """
        return self._current_time['M']

    @property
    def s(self) -> str:
        """ seconds """
        return self._current_time['S']

    @property
    def stamp(self) -> str:
        """ stamp """
        return self._current_time['STAMP']

    @property
    def default_format(self) -> str:
        """ default format """
        return f"{self.h}:{self.m}:{self.s} {self.stamp}"

    @staticmethod
    def in_format(formats: str, hour_diff: float) -> str:
        """ send date and time in full format using time module | DD - date | MM - month in digit | M - month in string |
        YYYY - 4 digit year | YY - 2 digit year | hh-24 - hour in 24 format | hh-12 - hour in 12 format | mm - minutes |
        AP - include AM/PM """

        diff_in_sec = hour_diff * 3600
        time_in_sec = time.time() + diff_in_sec
        format_ = (
            formats.replace("DD", "%d")
            .replace("MM", "%m")
            .replace("M", "%h")
            .replace("YYYY", "%Y")
            .replace("YY", "y")
            .replace("hh-24", "%H")
            .replace("hh-12", "%I")
            .replace("mm", "%M")
            .replace("AP", "%p")
        )
        date_time_ = time.strftime(format_, time.gmtime(time_in_sec))
        return date_time_


def user_friendly(id: int) -> bool:
    """ check user is owner or sudo user """
    if id == Config.OWNER_ID:
        return True
    elif id in Config.TRUSTED_SUDO_USERS or id in Config.SUDO_USERS:
        return True
    else:
        return False


def check_none(**kwargs) -> None:
    for one in kwargs.keys():
        if one is None:
            raise VarNotFoundException(one)
