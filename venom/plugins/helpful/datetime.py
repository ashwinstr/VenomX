 # datetime.py

from pytz import timezone as tz
from datetime import datetime, timedelta, timezone

from venom import venom, MyMessage, Config


@venom.trigger("dt")
async def date_time(_, message: MyMessage):
    " check date and time "
    tzone = Config.TIME_ZONE
    print(tz())
#    tz_ = timezone(offset=timedelta)
#    date_time_ = datetime.now(tz=tz_)
#    dt = date_time_.strftime("%d-%b, %Y %I:%M:%S %p</b> on <b>%A")
#    await message.edit(f"Current date and time are: <b>{dt}</b>")