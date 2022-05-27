# db.py

from venom.core.database import get_collection


class Collection:
    """ Collections """

    # basic collections
    TOGGLES = get_collection("TOGGLES") # has SUDO

    # sudo collections
    SUDO_USERS = get_collection("SUDO_USERS")
    TRUSTED_SUDO_USERS = get_collection("TRUSTED_SUDO_USERS")
    SUDO_CMD_LIST = get_collection("SUDO_CMD_LIST")

    # alive
    ALIVE_MEDIA = get_collection("ALIVE_MEDIA")

    # restart/update
    RESTART = get_collection("RESTART")
    UPDATE = get_collection("UPDATE")