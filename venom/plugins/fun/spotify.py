# spotify.py

from venom import venom, Config, MyMessage


@venom.trigger('spotdl')
async def spot_dl(_, message: MyMessage):
    " download from spotify "
    