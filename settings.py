####
##
#
#
"""
Вот такая в питоне нелепая инкапсуляция
that's sooo ridiculous encapsulation by python
"""

import os
import sys
import json
from os import environ

# import time
# import requests

from deta import Deta
from hashlib import sha1 as sha

from loguru import logger as log
from var_dump import var_dump


# from dotenv import dotenv_values
# config = dotenv_values(".env")    # do not work properly
from dotenv import load_dotenv

load_dotenv()

# Initialize with a Project Key
TG_TOKEN = environ.get("TG_TOKEN", "#_#")
TG_MAX_CONNECTION = int(environ.get("TG_MAX_CONNECTION", "40"))
TG_DROP_UPDATES = bool(environ.get("TG_DROP_UPDATES", None))
TG_TIMEOUT = int(environ.get("TG_TIMEOUT", "10"))
TG_MODE = environ.get("TG_MODE", "webhook")
TG_PARSE_MODE = environ.get("TG_PARSE_MODE", None)


DETA_PROJECT_KEY = environ.get("DETA_PROJECT_KEY", None)
DETA_DB_NAME = environ.get("DETA_DB_NAME", "nosqlite")

FILE_TOKEN = WEBHOOK_DOMAIN = WEBHOOK_PATH = WH_URL = WH_PATH = None

# telebot.polling updates types
ALLOWED_UPDATES = [
    "message",
    "edited_message",
    "channel_post",
    "edited_channel_post",
    "inline_query",
    "chosen_inline_result",
    "callback_query",
    "shipping_query",
    "poll",
    "poll_answer",
    "my_chat_member",
    "chat_member",
]


def HelloWorld():
    print("Hello World!")


if __name__ == "__main__":
    HelloWorld()
# else:
#     __all__ = ["config", "deta", "DB", "SESSION_DB", "sha", "log"]
