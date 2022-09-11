 # datetime.py

from pytz import timezone as tz, UnknownTimeZoneError, country_timezones as ct, country_names as cn
from datetime import datetime

from venom import venom, MyMessage, Config
from venom.helpers import paste_it

COUNTRY_LIST = ""

async def _init() -> None:
    list_ = ""
    for one in cn.keys():
        list_ += f"{one}: {cn.get(one)}\n"
    list_ = "LIST OF TIMEZONE:\n\n" + list_
    link_ = await paste_it(list_)
    global COUNTRY_LIST
    COUNTRY_LIST = link_


@venom.trigger(r'dt ?(\w*)?\s?(\d*)?')
async def date_time(_, message: MyMessage):
    " check date and time "
    if message.matches:
        match_ = message.matches[0]
        country = match_.group(1) or "in"
        country = country.upper()
        if country == "HELP":
            await message.reply(cn.keys())
            return await message.edit(f"Country list: **[LINK]({COUNTRY_LIST})**")
        num = match_.group(2) or 1
    try:
        tz_ = tz(zone=ct[country][int(num) - 1])
    except UnknownTimeZoneError:
        return await message.edit(f"`Unknown timezone.`\nSee country list **[HERE]({COUNTRY_LIST})**", del_in=5)
    except IndexError:
        text_ = f"#<b>INDEX_ERROR\n\n</b>Country <b>{country}</b>'s timezones:" + " [<b>{}</b>]\n"
        total = 0
        for one in ct[country]:
            total += 1
            text_ += f"{Config.BULLET_DOT}{total} - <b>{one}</b>\n"
        return await message.edit(text_.format(total))
    format_ = "%d-%b, %Y </b>at<b> %I:%M:%S %p</b> on <b>%A"
    dt_ = datetime.now().astimezone(tz_).strftime(format_)
    await message.edit(f"Timezone <b>({ct[country][int(num) - 1]})</b>: <b>{dt_}</b>")