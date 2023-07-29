# init/messages.py

import requests

from venom import Config, SecureConfig

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

    def __init__(self):
        base_url = "https://api.telegram.org/bot" + str(SecureConfig().BOT_TOKEN)
        self._SEND_URL = base_url + "/sendMessage?chat_id={}&text={}&parse_mode=markdown"
        self._EDIT_URL = base_url + "/editMessageText?chat_id={}&message_id={}&text={}&parse_mode=markdown"
        self._DEL_URL = base_url + "/deleteMessage?chat_id={}&message_id={}"

    def send_message(self, text: str, chat_id: int = Config.LOG_CHANNEL_ID) -> dict:
        resp_ = requests.get(self._SEND_URL.format(chat_id, text))
        json_ = resp_.json()
        return json_['result']

    def edit_message(self, message_id: int, text: str, chat_id: int = Config.LOG_CHANNEL_ID) -> dict:
        resp_ = requests.get(self._EDIT_URL.format(chat_id, message_id, text))
        json_ = resp_.json()
        return json_['result']

    def delete_message(self, message_id: int, chat_id: int = Config.LOG_CHANNEL_ID) -> dict:
        resp_ = requests.get(self._DEL_URL.format(chat_id, message_id))
        json_ = resp_.json()
        return json_


class ChangeInitMessage:

    def __init__(self) -> None:
        self.message_id = Config.START_MESSAGE_DICT['message_id']
        self.initial = InitMessages()

    def first_line(self) -> None:
        """ edit first line in Initial message """
        self.initial.edit_message(self.message_id, FIRST_MESSAGE)

    def second_line(self) -> None:
        """ edit second line in Initial message """
        self.initial.edit_message(self.message_id, SECOND_MESSAGE)

    def third_line(self) -> None:
        """ edit third line in Initial message """
        self.initial.edit_message(self.message_id, THIRD_MESSAGE)

    def exiting(self) -> None:
        """ stopping bot """
        try:
            self.initial.edit_message(self.message_id, LAST_MESSAGE)
        except requests.exceptions.ConnectionError:
            print("Failed sending exit message...")


Config.START_MESSAGE_DICT = InitMessages().send_message(INITIAL_MESSAGE)
