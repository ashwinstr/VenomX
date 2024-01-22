""" translate.py """

# import openai
from venom import venom, MyMessage, Config


MODEL = "gpt-3.5-turbo"
# openai.api_key = Config.OPENAI_API_KEY

LANGUAGES = {
    '-en': 'english',
    '-fr': 'french',
    '-gj': 'gujrati',
    '-hi': 'hindi',
    '-hing': 'hinglish',
    '-mr': 'marathi',
    '-tr': 'turkish'
}

Config().help_formatter(
    name=__name__,
    command='tr',
    flags=LANGUAGES,
    usage='Translate text',
    syntax='{tr}tr [reply to text|input text to translate]',
    sudo=True
)


@venom.trigger('tr')
async def translate_text(_, message: MyMessage):
    """ translate text """
    if not Config.OPENAI_API_KEY:
        return await message.edit("Get the api from openai.com first...")
    lang_code = message.flags[0] if len(message.flags) != 0 else "en"
    try:
        lang_to = LANGUAGES[lang_code]
    except KeyError:
        return await message.edit(f"<code>Please provide right language code...</code>\n"
                                  f"See {Config.CMD_TRIGGER}tr_codes for the language list.", del_in=5)
    await message.edit(f"<code>Translating to {lang_to}...</code>")
    if lang_to == "hinglish":
        content = f"'{message.filtered_input}', translate it into romanised hindi."
    else:
        content = f"'{message.filtered_input}', translate it to {lang_to}."
    resp = openai.ChatCompletion.create(
        model=MODEL,
        temperature=1,
        top_p=1,
        max_tokens=50,
        presence_penalty=0,
        frequency_penalty=0,
        messages=[
            {'role': 'system', 'content': f'You are an expert translator who translates the given content by user to {lang_to}.'},
            {'role': 'user', 'content': message.filtered_input}
        ]
    )
    out_text = resp['choices'][0]['message']['content']
    await message.edit(f"<code>{out_text}</code>")


Config().help_formatter(
    name=__name__,
    command='tr_codes',
    flags=None,
    usage='Check language codes',
    syntax='{tr}tr_codes',
    sudo=True
)


@venom.trigger('tr_code')
async def translate_languages(_, message: MyMessage):
    """ check language codes """


@venom.trigger('tr2')
async def palm_reader(_, message: MyMessage):
    """ testiing  """
