#####
##
#
#
"""databases &C"""

from uuid import uuid4, uuid1, uuid3, uuid5
from telebot import types
from deta import Deta

from settings import sha
from settings import DETA_PROJECT_KEY, DETA_DB_NAME

from dateparser import parse as dateparser

deta = Deta(DETA_PROJECT_KEY)
DB = deta.Base
# ACTION_DB = DB(DETA_DB_NAME)
# SESSION_DB = DB("SESSION")  #    PYSESSID


def id():
    return str(uuid4())


# def message_id(message: types.Update):
def message_id(message):
    return "{}:{}".format(message.from_user.id, message.chat.id)


# in python3 arg's order be like:
def key(*args, series=None, **kwargs):

    s = ""
    if isinstance(series, types.Update):
        s = message_id(series)
    if isinstance(series, (list, tuple, set)):
        # s = sorted(set(args+list(series)))
        s = sorted(series)
    if isinstance(series, (dict)):
        s = dict(sorted(series.items()))

    if not len(s):
        # if s is None:
        #         raise Exception("\db/ key")
        s = str(series)

    s = "{}:{}".format(s, hasher(*args, **kwargs))

    #     if len(args):
    #         s = "{}:{}".format(s, ":".join([a for a in args]))

    #     pp(args, kwargs)
    #     print("key", s)
    return s


def hasher(*args, **kwargs):
    return sha(str(list(args) + sorted(kwargs.items())).encode("utf8")).hexdigest()


# SESSION_KEY = db_hasher()
# Session = SESSION_DB.get(SESSION_KEY)
# var_dump(Session)
