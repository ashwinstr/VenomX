# datetime.py

import datetime

from venom import venom, MyMessage, Config


@venom.trigger("dt")
async def date_time(_, message: MyMessage):
    " check date and time "
    date_time_ = datetime.datetime.now()
    dt = date_time_.strftime("%d-%b, %Y %I:%M:%S %p</b> on <b>%A")
    await message.edit(f"Current date and time are: <b>{dt}</b>")