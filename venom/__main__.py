# main.py

from pyrogram.errors import AuthKeyDuplicated

from venom import logging, venom

_ERROR = "##### {} #####"
_LOG = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        venom.run()
    except AuthKeyDuplicated:
        msg_ = "STRING DUPLICATED, GENERATE NEW SESSION STRING"
        len_ = len(msg_)
        hash_ = "#"*(len_+12)
        _LOG.error(f"\n{hash_}\n{_ERROR.format(msg_)}\n{hash_}\n")
