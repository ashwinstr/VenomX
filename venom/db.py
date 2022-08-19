# db.py

from venom.core.database import get_collection


class Collection:
    """ Collections """

    # alive
    ALIVE_MEDIA = get_collection("ALIVE_MEDIA")

    # basic collections
    TOGGLES = get_collection("TOGGLES") # FBAN_TAG, F_DEL, KANGLOG, PM_GUARD, PM_TOG, SUDO, USER_IS_SELF

    # fbans
    FED_LIST = get_collection("FED_LIST")

    # loader
    TEMP_LOADED = get_collection("TEMP_LOADED")

    # pm guard
    ALLOWED_TO_PM = get_collection("ALLOWED_TO_PM")
    DISALLOWED_PM_COUNT = get_collection("DISALLOWED_PM_COUNT")
    
    # pm logger
    MSG_LIST = get_collection("MSG_LIST")

    # restart/update
    RESTART = get_collection("RESTART")
    UPDATE = get_collection("UPDATE")

    # sudo collections
    SUDO_USERS = get_collection("SUDO_USERS")
    TRUSTED_SUDO_USERS = get_collection("TRUSTED_SUDO_USERS")
    SUDO_CMD_LIST = get_collection("SUDO_CMD_LIST")
