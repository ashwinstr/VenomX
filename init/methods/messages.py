# init/messages.py
import time

import requests

from venom import Config

BASE_URL_ = "https://api.telegram.org/bot" + Config.BOT_TOKEN

SEND_URL_ = BASE_URL_ + "/sendMessage?chat_id={}&text={}&parse_mode=markdown"
EDIT_URL_ = BASE_URL_ + "/editMessageText?chat_id={}&message_id={}&text={}&parse_mode=markdown"
DEL_URL_ = BASE_URL_ + "/deleteMessage?chat_id={}&message_id={}"

# INITIAL_MESSAGE = """
# *Progress*:
#
# `Initialising bot...` ❕
# `Starting VenomX...` ❕
# `Loading initial functions...` ❕
# """

INITIAL_MESSAGE = """
`Initialising bot...` ❕ 
"""

# FIRST_MESSAGE = """
# *Progress*:
#
# `Initialised bot successfully.` ❗
# `Starting VenomX...` ❕
# `Loading initial functions...` ❕
# """

FIRST_MESSAGE = """
`Starting VenomX...` ❕
"""

# SECOND_MESSAGE = """
# *Progress*:
#
# `Initialised bot successfully.` ❗
# `Started VenomX successfully.` ❗
# `Loading initial functions...` ❕
# """

SECOND_MESSAGE = """
`Loading initial functions...` ❕
"""

# THIRD_MESSAGE = """
# `Initialised bot successfully.` ❗
# `Started VenomX successfully.` ❗
# `Loaded initial functions successfully.` ❗
# """

THIRD_MESSAGE = "`VenomX started successfully ❗`"

# LAST_MESSAGE = """
# `Initialised bot successfully.` ❗
# `Started VenomX successfully.` ❗
# `Loaded initial functions successfully.` ❗
#
# *VenomX has been stopped.* ❗❗❗
# """

LAST_MESSAGE = "*VenomX has been stopped.* ❗❗❗"


class InitMessages:

    def send_message(text: str, chat_id: int = Config.LOG_CHANNEL_ID) -> dict:
        resp_ = requests.get(SEND_URL_.format(chat_id, text))
        json_ = resp_.json()
        return json_['result']

    def edit_message(message_id: int, text: str, chat_id: int = Config.LOG_CHANNEL_ID) -> dict:
        resp_ = requests.get(EDIT_URL_.format(chat_id, message_id, text))
        json_ = resp_.json()
        return json_['result']

    def delete_message(message_id: int, chat_id: int = Config.LOG_CHANNEL_ID) -> dict:
        resp_ = requests.get(DEL_URL_.format(chat_id, message_id))
        json_ = resp_.json()
        return json_


class ChangeInitMessage():

    def __init__(self) -> None:
        self.message_id = Config.START_MESSAGE_DICT['message_id']

    def first_line(self) -> None:
        """ edit first line in Initial message """
        InitMessages.edit_message(self.message_id, FIRST_MESSAGE)

    def second_line(self) -> None:
        """ edit second line in Initial message """
        InitMessages.edit_message(self.message_id, SECOND_MESSAGE)

    def third_line(self) -> None:
        """ edit third line in Initial message """
        InitMessages.edit_message(self.message_id, THIRD_MESSAGE)

    def exiting(self) -> None:
        """ stopping bot """
        InitMessages.edit_message(self.message_id, LAST_MESSAGE)


Config.START_MESSAGE_DICT = InitMessages.send_message(INITIAL_MESSAGE)
