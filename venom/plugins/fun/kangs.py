# kangs.py ported from USERGE-X

import os
import io
from PIL import Image

from pyrogram import emoji
from pyrogram.enums import ParseMode
from pyrogram.errors import StickersetInvalid, YouBlockedUser
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from venom import venom, MyMessage, Config, Collection
from venom.helpers import plugin_name, Media_Info, runcmd

CHANNEL = venom.getCLogger(__name__)
TOG = Collection.TOGGLES
HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'fun', 'commands': []}

async def _init() -> None:
    found = await TOG.find_one({"_id": "KANGLOG"})
    if found:
        Config.KANGLOG = found["switch"]
    else:
        Config.KANGLOG = False


####################################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'kanglog',
        'flags': {
            '-c': 'check',
        },
        'usage': 'toggle logging in log channel or current chat',
        'syntax': '{tr}kanglog [optional flag]',
        'sudo': False
    }
)

@venom.trigger('kanglog')
async def kang_log(_, message: MyMessage):
    " toggle logging in log channel or current chat "
    if "-c" in message.flags:
        out_ = "ON" if Config.KANGLOG else "OFF"
        return await message.edit(f"Logging kang in channel is <b>{out_}</b>.", del_in=5)
    if Config.KANGLOG:
        Config.KANGLOG = False
        await TOG.update_one(
            {"_id": "KANGLOG"}, {"$set": {"switch": False}}, upsert=True
        )
    else:
        Config.KANGLOG = True
        await TOG.update_one(
            {"_id": "KANGLOG"}, {"$set": {"switch": True}}, upsert=True
        )
    out_ = "ON" if Config.KANGLOG else "OFF"
    await message.edit(f"Logging kang in channel is now <b>{out_}</b>.")

####################################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'kang',
        'flags': {
            '-s': 'without link',
            '-f': 'fast-forward video stickers'
        },
        'usage': 'kang sticker easily with userbot',
        'syntax': '{tr}kang [reply to sticker] [optional custom emoji] [optional pack number]',
        'sudo': True
    }
)

@venom.trigger('kang')
async def kang_ing(_, message: MyMessage):
    " kang stickers easily with userbot "
    user = await venom.get_me()
    replied = message.replied
    if Config.KANGLOG:
        await message.edit("`Kanging in log channel...`", del_in=1)
        kang_msg = await venom.send_message(Config.LOG_CHANNEL_ID, "`Processing...`")
    else:
        kang_msg = await message.edit("`Processing...`")
    media_ = None
    emoji_ = None
    is_anim = False
    is_video = False
    resize = False
    ff_vid = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
            replied.document.file_name
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
            replied.document.file_name
        elif replied.document and "video" in replied.document.mime_type:
            resize = True
            is_video = True
            ff_vid = True if "-f" in message.flags else False
        elif replied.animation:
            resize = True
            is_video = True
            ff_vid = True if "-f" in message.flags else False
        elif replied.video:
            resize = True
            is_video = True
            ff_vid = True if "-f" in message.flags else False
        elif replied.sticker:
            if not replied.sticker.file_name:
                await kang_msg.edit("`Sticker has no Name!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            is_video = replied.sticker.is_video
            if not (
                replied.sticker.file_name.endswith(".tgs")
                or replied.sticker.file_name.endswith(".webm")
            ):
                resize = True
                ff_vid = True if "-f" in message.flags else False
        else:
            await kang_msg.edit("`Unsupported File!`")
            return
        await kang_msg.edit(f"`Kanging sticker...`")
        media_ = await replied.download(file_name=f"{Config.DOWN_PATH}")
    else:
        await kang_msg.edit("`I can't kang that...`")
        return
    if media_:
        args = message.filtered_input.split()
        pack = 1
        if len(args) == 2:
            emoji_, pack = args
        elif len(args) == 1:
            if args[0].isnumeric():
                pack = int(args[0])
            else:
                emoji_ = args[0]

        if emoji_ and emoji_ not in (
            getattr(emoji, _) for _ in dir(emoji) if not _.startswith("_")
        ):
            emoji_ = None
        if not emoji_:
            emoji_ = "👁‍🗨"

        u_name = user.username
        u_name = "@" + u_name if u_name else user.first_name or user.id
        packname = f"a{user.id}_by_{user.username}_{pack}"
        custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s venom pack"
        packnick = f"{custom_packnick} vol.{pack}"
        cmd = "/newpack"
        if resize:
            media_ = await resize_photo(media_, is_video, ff_vid)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        if is_video:
            packname += "_video"
            packnick += " (Video)"
            cmd = "/newvideo"
        exist = False
        while True:
            try:
                exist = await message.client.send(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname), hash=0
                    )
                )
            except StickersetInvalid:
                exist = False
                break
            limit = 50 if (is_video or is_anim) else 120
            if exist.set.count >= limit:
                pack += 1
                packname = f"a{user.id}_by_userge_{pack}"
                packnick = f"{custom_packnick} Vol.{pack}"
                if is_anim:
                    packname += f"_anim{pack}"
                    packnick += f" (Animated){pack}"
                if is_video:
                    packname += f"_video{pack}"
                    packnick += f" (Video){pack}"
                await kang_msg.edit(
                    f"`Switching to Pack {pack} due to insufficient space`"
                )
                continue
            break
        if exist is not False:
            try:
                start_: MyMessage = await venom.send_message("Stickers", "/addsticker")
            except YouBlockedUser:
                return await kang_msg.edit("First **unblock** @Stickers bot.", del_in=5)
            except Exception as e:
                return await kang_msg.edit(("<b>ERROR:</b> %s", e), del_in=5)
            resp = await start_.wait()
            limit = "50" if is_anim else "120"
            while limit in resp.text:
                pack += 1
                packname = f"a{user.id}_by_{user.username}_{pack}"
                packnick = f"{custom_packnick} vol.{pack}"
                if is_anim:
                    packname += "_anim"
                    packnick += " (Animated)"
                if is_video:
                    packname += "_video"
                    packnick += " (Video)"
                await kang_msg.edit(
                    "`Switching to Pack "
                    + str(pack)
                    + " due to insufficient space`"
                )
                await resp.reply(packname)
                resp = await resp.wait()
                if resp.text == "Invalid pack selected.":
                    await resp.reply(cmd)
                    await resp.wait()
                    await resp.reply(packnick)
                    await resp.wait()
                    await resp.reply_document(media_)
                    await resp.wait()
                    await resp.reply(emoji_)
                    await resp.wait()
                    await resp.reply("/publish")
                    await resp.wait()
                    if is_anim:
                        await resp.reply(f"<{packnick}>", parse_mode=ParseMode.MARKDOWN)
                        await resp.wait()
                    await resp.reply("/skip")
                    await resp.wait()
                    await resp.reply(packname)
                    await resp.wait()
                    out = (
                        "__kanged__"
                        if "-s" in message.flags
                        else f"[kanged](t.me/addstickers/{packname})"
                    )
                    await kang_msg.edit(
                        f"**Sticker** {out} __in a Different Pack__**!**"
                    )
                    return
            await resp.reply_document(media_)
            resp = await resp.wait()
            if "Sorry, the file type is invalid." in resp.text:
                await kang_msg.edit(
                    "`Failed to add sticker, use` @Stickers "
                    "`bot to add the sticker manually.`"
                )
                return
            await resp.reply(emoji_)
            await resp.wait()
            await resp.reply("/done")
        else:
            await kang_msg.edit("`Making a new Pack...`")
            try:
                start_: MyMessage = await venom.send_message("Stickers", cmd)
            except YouBlockedUser:
                return await kang_msg.edit("First **unblock** @Stickers bot.")
            await start_.wait()
            await start_.reply(packnick)
            await start_.wait()
            await start_.reply_document(media_)
            resp = await start_.wait()
            if "Sorry, the file type is invalid." in resp.text:
                await kang_msg.edit(
                    "`Failed to add sticker, use` @Stickers "
                    "`bot to add the sticker manually.`"
                )
                return
            await resp.reply(emoji_)
            await resp.wait()
            await resp.reply("/publish")
            await resp.wait()
            if is_anim:
                await resp.reply(f"<{packnick}>")
                await resp.wait()
            await resp.reply("/skip")
            await resp.wait()
            await resp.reply(packname)
            await resp.wait()
        out = (
            "__kanged__"
            if "-s" in message.flags
            else f"[kanged](t.me/addstickers/{packname})"
        )
        await kang_msg.edit(f"**Sticker** {out}**!**")
        if os.path.exists(str(media_)):
            os.remove(media_)

async def resize_photo(media: str, video: bool, fast_forward: bool) -> str:
    """Resize the given photo to 512x512"""
    if video:
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
        _, error = await runcmd(cmd)
        os.remove(media)
        if error:
            await CHANNEL.log(error)
        return resized_video

    image = Image.open(media)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))

    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = "sticker.png"
    image.save(resized_photo)
    os.remove(media)
    return resized_photo