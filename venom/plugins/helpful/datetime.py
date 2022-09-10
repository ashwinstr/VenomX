 # datetime.py

from pytz import timezone as tz, all_timezones, UnknownTimeZoneError
from datetime import datetime, timedelta, timezone

from venom import venom, MyMessage, Config


@venom.trigger("dt")
async def date_time(_, message: MyMessage):
    " check date and time "
    tzone = message.input_str or Config.TIME_ZONE
    await message.edit_or_send_as_file(all_timezones)
    try:
        tz_ = tz(zone=tzone)
    except UnknownTimeZoneError:
        return await message.edit("`Unknown timezone.`", del_in=5)
    format_ = "%d-%b, %Y %I:%M:%S %p</b> on <b>%A"
    dt_ = datetime.now().astimezone(tz(zone=tzone)).strftime(format_)
    await message.edit(f"Date time as per <b>{tzone}</b> is: <b>{dt_}</b>")
#    dt = date_time_.strftime("%d-%b, %Y %I:%M:%S %p</b> on <b>%A")
#    await message.reply(datetime.now().astimezone(tz(zone=tzone)).strftime())
#    await message.edit(f"Current date and time are: <b>{dt}</b>")