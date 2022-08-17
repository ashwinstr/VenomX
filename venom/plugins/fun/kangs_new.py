# kangs_new.py

import os
import io
from PIL import Image

from pyrogram.errors import StickersetInvalid
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.functions.stickers import CreateStickerSet, AddStickerToSet
from pyrogram.raw.types import (
    InputStickerSetShortName,
    InputStickerSetItem,
    InputDocument
)
from pyrogram.file_id import FileId

from venom import venom, MyMessage, Config

@venom.trigger('nkang')
async def new_kang(_, message: MyMessage):
    " new kang "
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to sticker or potential sticker...`", del_in=5)
    user = await venom.get_me()
    bot_ = await venom.bot.get_me()
    emoji_ = None
    is_anim = False
    is_video = False
    resize = False
    ff_vid = False
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
        if reply_.document:
            sticker_ = await venom.send_document(bot_.username, resized_)
        elif reply_.photo:
            sticker_ = await venom.send_sticker(bot_.username, resized_)
        file_ = FileId.decode(sticker_.sticker.file_id)
    await message.edit("`Kanging...`")
    pack = 1
    u_name = bot_.username
    u_name = "@" + u_name if u_name else bot_.first_name or bot_.id
    packname = f"a{bot_.id}_pack{pack}_by_{bot_.username}"
    custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s venom pack"
    packnick = f"{custom_packnick} vol.{pack}"
    old_pack = True
    try:
        await venom.invoke(GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname), hash=0))
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
                    emoji=emoji_ or "👁‍🗨"
                )
            )
        )
        return
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
    resized_photo.name = "sticker.webp"
    image.save(resized_photo, "WEBP")
    os.remove(media)
    return resized_photo