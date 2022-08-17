# kangs_new.py

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
    await message.edit("`Kanging...`")
    pack = 1
    u_name = user.username
    u_name = "@" + u_name if u_name else user.first_name or user.id
    packname = f"a{user.id}_by_{user.username}_{pack}"
    custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s venom pack"
    packnick = f"{custom_packnick} vol.{pack}"
    old_pack = True
    try:
        pack_: StickerSet = await venom.invoke(GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname), hash=0))
    except StickersetInvalid:
        old_pack = False
    file_ = FileId.decode(reply_.sticker.file_id)
    if old_pack:
        await venom.bot.invoke(
            AddStickerToSet(
                stickerset=InputStickerSetShortName(
                    short_name=pack_.set.short_name
                ),
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
            user_id=(await venom.resolve_peer((await venom.bot.get_me()).id)),
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
