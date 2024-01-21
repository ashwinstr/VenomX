from .message import SendMessage, EditMessageText
from .decorators import Trigger, OnMessage
from .channels import GetCLogger
from .utils import Listener, DefaultListener


class Methods(SendMessage, EditMessageText, Trigger, OnMessage, GetCLogger, Listener):
    """ methods """
