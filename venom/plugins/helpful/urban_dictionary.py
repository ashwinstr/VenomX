# urban_dictionary.py

import asyncurban as urban

from pyrogram.enums import ParseMode

from venom import venom, Config, plugin_name, MyMessage

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'ud',
        'flags': None,
        'usage': 'Check urban dictionary for a term.',
        'syntax': '{tr}ud [term]',
        'sudo': True
    }
)


@venom.trigger('ud')
async def urban_dict(_, message: MyMessage):
    """ check urban dictionary for a term """
    term_ = message.input_str
    if not term_:
        return await message.edit("`Provide input term to search in urban dictionary...`", del_in=5)
    dict_ = urban.UrbanDictionary()
    try:
        result = await dict_.get_word(term_)
    except urban.WordNotFoundError:
        return await message.edit(f"`Nothing found for {term_}...`", del_in=5)
    msg_ = f"""
--Result found for **{term_}**--:

**Text**: {result.word}
**Meaning**: `{result.definition}`

**Example**: __{result.example}__
"""
    await message.edit(msg_, parse_mode=ParseMode.MARKDOWN)