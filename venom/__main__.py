# main.py

import requests

from pyrogram.errors import AuthKeyDuplicated, FloodWait

from venom import logging, venom, Config

_ERROR = "##### {} #####"
_LOG = logging.getLogger(__name__)
_URL = (
    f"https://api.telegram.org/bot{Config.BOT_TOKEN}"
    f"/sendMessage?chat_id={Config.LOG_CHANNEL_ID}&text=`Starting VenomX...`&parse_mode=markdown"
)


if __name__ == "__main__":
    requests.post(_URL)
    try:
        venom.run()
    except AuthKeyDuplicated:
        msg_ = "STRING EXPIRED, GENERATE NEW SESSION STRING"
        len_ = len(msg_)
        hash_ = "#"*(len_+12)
        _LOG.error(f"\n{hash_}\n{_ERROR.format(msg_)}\n{hash_}\n")
    except FloodWait as e:
        print(f"Please wait for {e.value} seconds...")
