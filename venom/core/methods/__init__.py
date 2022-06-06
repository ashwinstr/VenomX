
from .message import SendMessage, EditMessageText
from .decorators import Trigger
from .channels import GetCLogger



class Methods(SendMessage, EditMessageText, Trigger, GetCLogger):
    """ methods """