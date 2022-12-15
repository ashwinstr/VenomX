from .message import SendMessage, EditMessageText, Listen
from .decorators import Trigger, OnMessage
from .channels import GetCLogger


class Methods(SendMessage, EditMessageText, Listen, Trigger, OnMessage, GetCLogger):
    """ methods """
