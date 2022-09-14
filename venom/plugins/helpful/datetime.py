 # datetime.py

from pytz import timezone as tz, UnknownTimeZoneError, country_timezones as ct, country_names as cn
from datetime import datetime

from venom import venom, MyMessage, Config
from venom.helpers import paste_it, plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}
COUNTRY_LIST = ""

async def _init() -> None:
    list_ = ""
    for one in cn.keys():
        total = 0
        list_ += f"{one}: {cn.get(one)}\n"
        try:
            for two in ct[one]:
                total += 1
                list_ += f"{total} {two}\n"
        except KeyError:
            pass
        list_ += "\n"
    list_ = "LIST OF TIMEZONE:\n\n" + list_
    link_ = await paste_it(list_)
    global COUNTRY_LIST
    COUNTRY_LIST = link_

#########################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'dt',
        'flags': None,
        'usage': 'Check time and date',
        'syntax': (
            '{tr}dt [country code] [timezone number]\n'
            'see help with "{tr}dt help"'
        ),
        'sudo': True
    }
)

@venom.trigger(r'dt ?(\w*)?\s?(\d*)?')
async def date_time(_, message: MyMessage):
    " check date and time "
    if message.matches:
        match_ = message.matches[0]
        country = match_.group(1) or "in"
        country = country.upper()
        if country == "HELP":
            return await message.edit(f"Country list: **[LINK]({COUNTRY_LIST})**")
        num = match_.group(2) or 1
    try:
        tz_ = tz(zone=ct[country][int(num) - 1])
    except UnknownTimeZoneError:
        return await message.edit(f"`Unknown timezone.`\nSee country list **[HERE]({COUNTRY_LIST})**", del_in=5)
    except IndexError:
        text_ = f"#<b>INDEX_ERROR</b>\n\nCountry <b>{country}</b>'s timezones:" + " [<b>{}</b>]\n"
        total = 0
        for one in ct[country]:
            total += 1
            text_ += f"{Config.BULLET_DOT}{total} - <b>{one}</b>\n"
        return await message.edit(text_.format(total))
    except KeyError:
        text_ = f"#<b>KEY_ERROR</b>\n\nWrong country code <b>{country}</b>\nSee country codes **[HERE]({COUNTRY_LIST})**"
        return await message.edit(text_)
    format_ = (
        "<b>Date:</b> `%d-%b-%Y` `%A`\n"
        "<b>Time:</b> `%I:%M:%S %p`"
    )
    dt_ = datetime.now().astimezone(tz_).strftime(format_)
    await message.edit(f"Timezone <b>{cn.get(country)}</b>({ct[country][int(num) - 1]}):\n{dt_}")
