# meaning.py

from PyDictionary import PyDictionary

from venom import venom, MyMessage, Config, plugin_name

CHANNEL = venom.getCLogger(__name__)
HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}

########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'mng',
        'flags': None,
        'usage': 'Find meaning of words',
        'syntax': '{tr}mng [word]',
        'sudo': True
    }
)


@venom.trigger('mng')
async def meaning_wrd(_, message: MyMessage):
    """ find meaning of words """
    await message.edit("`Searching for meaning...`")
    word = message.input_str or message.reply_to_message.text
    if not word:
        await message.edit("No input!")
    else:
        dictionary = PyDictionary()
        words = dictionary.meaning(word)
        output = f"**Word :** __{word}__\n"
        try:
            for a, b in words.items():
                output = output + f"\n**{a}**\n"
                for i in b:
                    output = output + f"• __{i}__\n"
            await message.edit(output)
        except Exception as e:
            await CHANNEL.log(str(e))
            await message.edit(f"Couldn't fetch meaning of {word}")