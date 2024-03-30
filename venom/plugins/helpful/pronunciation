# pronuntiation.py

import json
import unicodedata
from googletrans import LANGUAGES, Translator

from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from venom import venom
from venom.helpers import VenomDecorators

trans = Translator()

########################################################################################################################


@venom.bot.on_inline_query()
@VenomDecorators.inline_checker(owner=True)
async def pro_nunciation(_, i_q: InlineQuery):
    " inline pronunciation "
    iq = i_q.query
    split_q = iq.split(" ", maxsplit=2)
    results = []
    if len(split_q) == 3 and split_q[0] == "pro":
        langs = ["auto", split_q[1]]
        if langs[1] not in LANGUAGES.keys():
            langs_str = json.dumps(LANGUAGES, indent=4)
            results.append(
                InlineQueryResultArticle(
                    title="SUPPORTED LANGUAGES.",
                    input_message_content=InputTextMessageContent("Invalid language code, check [LINK]("
                                                                  "https://telegra.ph/By-Kakashi-HTK-08-07) for "
                                                                  "language codes.")
                )
            )
        else:
            translation = trans.translate(split_q[2], dest=langs[1], src=langs[0])
            pronun = translation.pronunciation
            if pronun == split_q[2]:
                pronun = translation.text
            else:
                pronun = unicodedata.normalize("NFKD", pronun).encode("ascii", "ignore").decode('utf-8')
            target_lang = (LANGUAGES[langs[1]]).upper()
            if not pronun:
                return
            results.append(
                InlineQueryResultArticle(
                    title="Pronunciation.",
                    description=f"{target_lang}\n{pronun}",
                    input_message_content=InputTextMessageContent(pronun),
                    thumb_url="https://telegra.ph/file/34b74cebb26d76ef23378.jpg"
                )
            )
        if len(results) != 0:
            await i_q.answer(results=results, cache_time=1)