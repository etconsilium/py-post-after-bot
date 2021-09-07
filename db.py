#####
##
#
#
"""databases &C"""

import os
import json

from hashlib import sha1
from dotenv import load_dotenv
from dotenv import dotenv_values
from loguru import logger as log
from var_dump import var_dump

from telebot import types

load_dotenv(".env")
config = dotenv_values(".env")

from deta import Deta

deta = Deta(os.getenv("DETA_PROJECT_KEY"))
DETA_DB_NAME = os.getenv("DETA_DB_NAME", "#_#")
DB = deta.Base(DETA_DB_NAME)
SESSION_DB = deta.Base("SESSION")  #    PYSESSID


def db_id(message: types.Update):
    return (
        #         "{}:{}".format(message["from"]["id"], message["chat"]["id"]).encode("utf8")
        "{}:{}".format(message.from_user.id, message.chat.id)
    )


def db_key(series=None, *args):
    s = ''
    if isinstance(series, types.Update):
        s = db_id(series)
    if type(series) in (list,tuple):
        s = str(sorted(series))
    if type(series) is dict:
        s = str(dict(sorted(series.items())))
    if type(series) is not str:
        # if s is None:
        raise Exception("\db/")
        
    if (len(kwargs)):
        s="{}:{}".format(s, join(':', [for a in args]))
    return s


def db_hash(**kwargs):
    var_dump(kwargs)
    return sha1(s.encode("utf8")).hexdigest()


# SESSION_KEY = db_hash()
# Session = SESSION_DB.get(SESSION_KEY)
# var_dump(Session)
