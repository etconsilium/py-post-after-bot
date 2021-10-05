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
            kwargs['id']
            if 'id' in kwargs
            else (
                args[0]
                if len(args) and not isinstance(args, (list, tuple, set, dict))
                else db_id()
            )
        )
        self.amount = 1 + int(self.amount if self.amount is not None else 0)
        self.last_connect = dateparser("now")
        # session.last_command = ""


pass


# SESSION = Session()
