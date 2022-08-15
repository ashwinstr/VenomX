
from .message import SendMessage, EditMessageText, Listen
from .decorators import Trigger
from .channels import GetCLogger



class Methods(SendMessage, EditMessageText, Listen, Trigger, GetCLogger):
    """ methods """