# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.
# Ported to Venom by Ryuk

import subprocess
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from pyrogram.enums import ParseMode
from requests import get
from venom import Config, MyMessage, venom
from venom.helpers import plugin_name

HELP = Config.HELP[plugin_name(__name__)] = {"type": "tools", "commands": []}


HELP["commands"].append(
    {
        "command": "neofetch",
        "about": "Neofetch is a command-line system information tool",
        "description": "displays information about your operating system, software and hardware in an aesthetic and visually pleasing way.",
        "usage": " {tr}neofetch",
        "flags": {"-img": "To Get output as Image"},
        "syntax": ["{tr}neofetch", "{tr}neofetch -img"],
        "sudo": True,
    },
)


@venom.trigger("neofetch")
async def neofetch_(_, message: MyMessage):
    flags_ = message.flags
    msg_ = await message.edit("Getting System Info ...")
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    if "-img" in flags_:
        await msg_.delete()
        await venom.send_photo(
            message.chat.id, await neo_image(), reply_to_message_id=reply_id
        )
    else:
        await msg_.edit(
            "<code>{}</code>".format(
                subprocess.run(
                    "neofetch --stdout", shell=True, capture_output=True
                ).stdout.decode("utf-8")
            ),
            parse_mode=ParseMode.HTML,
        )


async def neo_image():
    neofetch = subprocess.run(
        "neofetch --stdout", shell=True, capture_output=True
    ).stdout.decode("utf-8")
    font_color = (255, 42, 38)  # Red
    white = (255, 255, 255)
    if "Debian" in neofetch:
        base_pic = "https://telegra.ph/file/1f62cbef3fe8e24afc6f7.jpg"
    elif "Kali" in neofetch:
        base_pic = "https://i.imgur.com/iBJxExq.jpg"
        font_color = (87, 157, 255)  # Blue
    else:
        base_pic = "https://telegra.ph/file/f3191b7ecdf13867788c2.jpg"
    font_url = (
        "https://raw.githubusercontent.com/code-rgb/AmongUs/master/FiraCode-Regular.ttf"
    )
    me = await venom.get_me()
    kakashi = [1156425647, 1013414037]
    if me.id in kakashi:
        base_pic = "https://telegra.ph/file/6cdadf4baddb83abfbed9.png"
    photo = Image.open(BytesIO(get(base_pic).content))
    drawing = ImageDraw.Draw(photo)
    font = ImageFont.truetype(BytesIO(get(font_url).content), 14)
    x = 0
    y = 0
    for u_text in neofetch.splitlines():
        if ":" in u_text:
            ms = u_text.split(":", 1)
            drawing.text(
                xy=(315, 45 + x),
                text=ms[0] + ":",
                font=font,
                fill=font_color,
            )
            drawing.text(
                xy=((8.5 * len(ms[0])) + 315, 45 + x), text=ms[1], font=font, fill=white
            )
        else:
            color = font_color if y == 0 else white
            drawing.text(xy=(315, 53 + y), text=u_text, font=font, fill=color)
        x += 20
        y += 13
    new_pic = BytesIO()
    photo = photo.resize(photo.size, Image.ANTIALIAS)
    photo.save(new_pic, format="png")
    new_pic.name = "NeoFetch.png"
    return new_pic
