# weather plugin

import json
from datetime import datetime

import aiohttp
from pyrogram.enums import ParseMode
from pytz import country_names as c_n
from pytz import country_timezones as c_tz
from pytz import timezone as tz

from venom import Config, MyMessage, venom

CHANNEL = venom.getCLogger(__name__)


async def get_tz(con):
    """Get time zone of the given country
    Credits: @aragon12 and @zakaryan2004
    """
    for c_code in c_n:
        if con == c_n[c_code]:
            return tz(c_tz[c_code][0])
    try:
        if c_n[con]:
            return tz(c_tz[con][0])
    except KeyError:
        return

########################################################################################################################


@venom.trigger('weather')
async def weather_get(message: MyMessage):
    """ this function can get weather info """
    owm_api = Config.OPEN_WEATHER_MAP
    if not owm_api:
        await message.edit(
            "<code>Oops!!! Get the API from</code> "
            "<a href='https://openweathermap.org'>HERE</a> "
            "<code>& add it to config vars</code> (<code>OPEN_WEATHER_MAP</code>)",
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
            del_in=0,
        )
        return

    app_id = owm_api

    if not message.input_str:
        city_ = Config.WEATHER_DEFCITY
        if not city_:
            await message.edit("`Please specify a city or set one as default!`", del_in=5)
            return
    else:
        city_ = message.input_str

    timezone_countries = {
        timezone: country
        for country, timezones in c_tz.items()
        for timezone in timezones
    }

    if "," in city_:
        new_city = city_.split(",")
        if len(new_city[1]) == 2:
            city_ = new_city[0].strip() + "," + new_city[1].strip()
        else:
            country = await get_tz((new_city[1].strip()).title())
            try:
                countrycode = timezone_countries[str(country)]
            except KeyError:
                await message.edit("`Invalid country.`", del_in=0)
                return
            city_ = new_city[0].strip() + "," + countrycode.strip()

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_}&appid={app_id}"
    async with aiohttp.ClientSession() as ses:
        async with ses.get(url) as res:
            req_status = res.status
            res_text = await res.text()
    result = json.loads(res_text)

    if req_status != 200:
        await message.edit(r"`Invalid country...`", del_in=0)
        return

    city_name = result["name"]
    cur_temp = result["main"]["temp"]
    humidity = result["main"]["humidity"]
    min_temp = result["main"]["temp_min"]
    max_temp = result["main"]["temp_max"]
    desc = result["weather"][0]
    desc = desc["main"]
    country = result["sys"]["country"]
    sunrise = result["sys"]["sunrise"]
    sunset = result["sys"]["sunset"]
    wind = result["wind"]["speed"]
    wind_dir = result["wind"]["deg"]

    ctime_zone = tz(c_tz[country][0])
    time = datetime.now(ctime_zone).strftime("%A, %I:%M %p")
    full_c_n = c_n[f"{country}"]
    # dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    #        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    div = 360 / len(dirs)
    funmath = int((wind_dir + (div / 2)) / div)
    fin_dir = dirs[funmath % len(dirs)]
    km_ph = str(wind * 3.6).split(".")
    mph = str(wind * 2.237).split(".")

    def fahrenheit(f):
        temp = str(((f - 273.15) * 9 / 5 + 32)).split(".")
        return temp[0]

    def celsius(c):
        temp = str((c - 273.15)).split(".")
        return temp[0]

    def sun(unix):
        return datetime.fromtimestamp(unix, tz=ctime_zone).strftime("%I:%M %p")

    await message.edit(
        f"**Temperature:** `{celsius(cur_temp)}°C | {fahrenheit(cur_temp)}°F`\n"
        + f"**Min. Temp.:** `{celsius(min_temp)}°C | {fahrenheit(min_temp)}°F`\n"
        + f"**Max. Temp.:** `{celsius(max_temp)}°C | {fahrenheit(max_temp)}°F`\n"
        + f"**Humidity:** `{humidity}%`\n"
        + f"**Wind:** `{km_ph[0]} kmh | {mph[0]} mph, {fin_dir}`\n"
        + f"**Sunrise:** `{sun(sunrise)}`\n"
        + f"**Sunset:** `{sun(sunset)}`\n\n\n"
        + f"**{desc}**\n"
        + f"`{city_name}, {full_c_n}`\n"
        + f"`{time}`"
    )
    await CHANNEL.log(f"Checked `{city_}` weather results...")
