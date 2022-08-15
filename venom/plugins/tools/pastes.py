# pastes.py

from pastypy import Paste

import os

from venom import venom, MyMessage, Config

@venom.trigger('paste')
async def past_es(_, message: MyMessage):
    " paste text to pasty.lus "
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to text...`", del_in=5)
    if not reply_.text and not reply_.caption and not reply_.document:
        return await message.edit("`Reply to text message or document...`", del_in=5)
    if reply_.document:
        if not reply_.document.file_name.endswith((".txt", ".py")):
            return await message.edit("`Document type not supported...`", del_in=5)
        await message.edit("`Downloading document...`")
        down_ = await reply_.download()
        with open(down_, "r") as file_:
            content_ = file_.read()
        os.remove(down_)
    else:
        content_ = reply_.text or reply_.caption
    paste_ = Paste(content=content_)
    paste_.save()
    link_ = paste_.url
    await message.edit(f"Pasted to <b>PastyLus</b>\n<b>Link:</b> [URL]({link_})")