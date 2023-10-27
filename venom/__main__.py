# main.py

import logging
import time

from pyrogram.errors import AuthKeyDuplicated, FloodWait

from init import ChangeInitMessage
from venom import venom
from venom.core.database import _close_db

_ERROR = "##### {} #####"
_LOG = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        ChangeInitMessage().first_line()
        venom.run()
        ChangeInitMessage().exiting()
    except AuthKeyDuplicated:
        msg_ = "STRING EXPIRED, GENERATE NEW SESSION STRING"
        len_ = len(msg_)
        hash_ = "#"*(len_+12)
        _LOG.error(f"\n{hash_}\n{_ERROR.format(msg_)}\n{hash_}\n")
    except FloodWait as e:
        print(f"Please wait for {e.value} seconds...")
        time.sleep(e.value)
    except TimeoutError:
        _close_db()
        