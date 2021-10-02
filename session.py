####
##
#
#
from db import dateparser, strdateparser, id as db_id
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
        super().__init__(*args, **kwargs)
        self.id = str(
            kwargs['id'] if 'id' in kwargs else (args[0] if len(args) else db_id())
        )
        self.last_connect = dateparser("now")


pass


SESSION = Session()
