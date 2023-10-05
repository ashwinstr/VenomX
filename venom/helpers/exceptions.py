# exceptions.py
# ported from USERGE-X fork UX-jutsu

class ProcessCancelled(Exception):
    """ Raise if thread has been terminated. """


class VarNotFoundException(Exception):
    """ Raised when required environmental variable is not found. """

    def __init__(self, var):
        print(f"{var} var not provided... Bot cannot start.")