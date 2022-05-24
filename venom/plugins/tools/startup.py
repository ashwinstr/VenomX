# startup.py

from venom import venom

CHANNEL = venom.getCLogger(__name__)


async def _init() -> None:
    await CHANNEL.log("### VenomX has started successfully. ###")