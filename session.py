####
##
#
#
from db import strdateparser
from models import BasicModel, Record

# class Session(BasicModel):
class Session(Record):
    """
    classdocs
    """

    _save_on_exit = True
    _tablename = "SESSION"

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        #         super().__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)

        self.last_connect = strdateparser("now")


pass
