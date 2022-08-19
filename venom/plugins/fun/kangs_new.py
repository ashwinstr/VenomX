# kangs_new.py

import os
import asyncio
import io
from PIL import Image

from pyrogram import filters
from pyrogram.errors import StickersetInvalid
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.functions.stickers import CreateStickerSet, AddStickerToSet
from pyrogram.raw.types import (
    InputStickerSetShortName,
    InputStickerSetItem,
    InputDocument,
    StickerSet
)
from pyrogram.file_id import FileId

from venom import venom, MyMessage, Config
from venom.helpers import Media_Info, runcmd

CHANNEL = venom.getCLogger(__name__)


@venom.trigger('nkang')
async def new_kang(_, message: MyMessage):
    " new kang "
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to sticker or potential sticker...`", del_in=5)
    user = await venom.get_me()
    bot_ = await venom.bot.get_me()
    pack = 1
    u_name = bot_.username
    u_name = "@" + u_name if u_name else bot_.first_name or bot_.id
    packname = f"a{bot_.id}_pack{pack}_by_{bot_.username}"
    custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s venom pack"
    packnick = f"{custom_packnick} vol.{pack}"
    emoji_ = None
    is_anim = False
    is_video = False
    old_pack = True
    try:
        pack: StickerSet = await venom.bot.invoke(GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname), hash=0))
    except StickersetInvalid:
        old_pack = False
    if reply_.sticker:
        emoji_ = reply_.sticker.emoji
        is_anim = reply_.sticker.is_animated
        is_video = reply_.sticker.is_video
        file_ = FileId.decode(reply_.sticker.file_id)
    elif reply_.video or reply_.animation:
        is_video = True
    elif reply_.photo or (reply_.document and reply_.document.file_name.endswith((".png", ".webp"))):
        await message.edit("`Downloading...`")
        down_ = await reply_.download(Config.DOWN_PATH)
        resized_ = resize_photo(down_)
        await venom.send_document(bot_.username, resized_, caption="#KANG")
        await asyncio.sleep(3)
        return await message.edit(f"<i>Sticker will be kanged...</i>\n<i>Check [<b>HERE</b>](t.me/addstickers/{packname}).")
    elif (reply_.document and reply_.document.file_name.endswith((".mp4", ".webm"))):
        is_video = True
        file_ = FileId.decode(file_id=reply_.document.file_id)
    if is_video:
        await message.edit("`Downloading...`")
        down_ = await reply_.download(Config.DOWN_PATH)
        converted_vid = await convert_video(down_)
        await venom.send_document(bot_.username, converted_vid, caption="#KANG")
        await asyncio.sleep(3)
        return await message.edit(f"<i>Sticker will be kanged...</i>\n<i>Check [<b>HERE</b>](t.me/addstickers/{packname}).")
    await message.edit("`Kanging...`")
    if old_pack:
        await venom.bot.invoke(
            AddStickerToSet(
                stickerset=InputStickerSetShortName(short_name=packname),
                sticker=InputStickerSetItem(
                    document=InputDocument(
                        id=file_.media_id,
                        access_hash=file_.access_hash,
                        file_reference=file_.file_reference
                    ),
                    emoji=emoji_ or "👁‍🗨"
                )
            )
        )
    else:
        await venom.bot.invoke(
            CreateStickerSet(
                user_id=await venom.resolve_peer(user.id),
                title=packnick,
                short_name=packname,
                stickers=[InputStickerSetItem(
                    document=InputDocument(
                        id=file_.media_id,
                        access_hash=file_.access_hash,
                        file_reference=file_.file_reference
                    ),
                    emoji=emoji_ or "👁‍🗨"
                )],
                animated=is_anim,
                videos=is_video
            )
        )
    await message.edit(f"Sticker <b>kanged</b>.\n<a href='t.me/addstickers/{packname}'>HERE</a>")


def resize_photo(media: str) -> str:
    " resize photo to make sticker "
    image = Image.open(media)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))

    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(media)
    return resized_photo

async def convert_video(media: str, fast_forward: bool = True) -> str:
    " convert video to make it sticker "
    info_ = Media_Info.data(media)
    width = info_["pixel_sizes"][0]
    height = info_["pixel_sizes"][1]
    sec = info_["duration_in_ms"]
    s = round(float(sec)) / 1000

    if height == width:
        height, width = 512, 512
    elif height > width:
        height, width = 512, -1
    elif width > height:
        height, width = -1, 512

    resized_video = f"{media}.webm"
    if fast_forward:
        if s > 3:
            fract_ = 3 / s
            ff_f = round(fract_, 2)
            set_pts_ = ff_f - 0.01 if ff_f > fract_ else ff_f
            cmd_f = f"-filter:v 'setpts={set_pts_}*PTS',scale={width}:{height}"
        else:
            cmd_f = f"-filter:v scale={width}:{height}"
    else:
        cmd_f = f"-filter:v scale={width}:{height}"
    fps_ = float(info_["frame_rate"])
    fps_cmd = "-r 30 " if fps_ > 30 else ""
    cmd = f"ffmpeg -i {media} {cmd_f} -ss 00:00:00 -to 00:00:03 -an -c:v libvpx-vp9 {fps_cmd}-fs 256K {resized_video}"
    _, error, __, ___ = await runcmd(cmd)
    os.remove(media)
    if error:
        await CHANNEL.log(error)
    return resized_video

############################################################################################################################################

@venom.bot.on_message(
    filters.user(Config.OWNER_ID)
    & filters.regex(r"^\#KANG$")
    & filters.private
    & filters.document,
    group=3
)
async def kang_bot(_, message):
    " kang with bot's help in pm "
    message: MyMessage = MyMessage.parse(message)
    doc_ = message.document
    file_ = FileId.decode(file_id=doc_.file_id)
    bot_ = await venom.bot.get_me()
    user = await venom.get_me()
    pack = 1
    u_name = bot_.username
    u_name = "@" + u_name if u_name else bot_.first_name or bot_.id
    packname = f"a{bot_.id}_pack{pack}_by_{bot_.username}"
    custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s venom pack"
    packnick = f"{custom_packnick} vol.{pack}"
    is_vid = False
    if message.document.file_name.endswith((".webm", ".mp4", ".gif")):
        is_vid = True
    if is_vid:
        packname = f"a{bot_.id}_vid_pack{pack}_by_{bot_.username}"
        packnick += "_vid"
    emoji_ = "👁‍🗨"
    old_pack = True
    try:
        await venom.bot.invoke(GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname), hash=0))
    except StickersetInvalid:
        old_pack = False
    if old_pack:
        await venom.bot.invoke(
            AddStickerToSet(
                stickerset=InputStickerSetShortName(short_name=packname),
                sticker=InputStickerSetItem(
                    document=InputDocument(
                        id=file_.media_id,
                        access_hash=file_.access_hash,
                        file_reference=file_.file_reference
                    ),
                    emoji=emoji_
                )
            )
        )
    else:
        await venom.bot.invoke(
            CreateStickerSet(
                user_id=await venom.resolve_peer(user.id),
                title=packnick,
                short_name=packname,
                stickers=[InputStickerSetItem(
                    document=InputDocument(
                        id=file_.media_id,
                        access_hash=file_.access_hash,
                        file_reference=file_.file_reference
                    ),
                    emoji=emoji_
                )]
            )
        )
    await message.edit(f"Sticker <b>kanged</b>.\n<a href='t.me/addstickers/{packname}'>HERE</a>")