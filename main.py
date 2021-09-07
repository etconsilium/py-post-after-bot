#!/usr/bin/env python3
####
##
##
#
"""
телеграмный бот
 * автоответчик: сохраняет и показывает сообщения
 * анонимизатор: в процессе разработки идея отошла на второй план

код иллюстрирует, как не надо писать код
также содержит примеры вариантов реализации (в комментариях)
  и хаков, которые описаны в документации, но их применение недостаточно ясно
"""

# pylint:    disable=e0401
# pylint:    disable=c0112,c0116

# import time
# import requests
import os
import sys
import json

from hashlib import sha1
from dotenv import load_dotenv
from dotenv import dotenv_values
from loguru import logger as log
from var_dump import var_dump

# from tqdm import tqdm

import telebot
from telebot import TeleBot
from telebot import apihelper
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


from fastapi import FastAPI
from fastapi import Body
from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

# from fastapi.requests import Session  #   notfound
from requests import Session

from deta import Deta

# from deta import FetchResponse    #    notfound


FILE_TOKEN = WEBHOOK_DOMAIN = WEBHOOK_PATH = WH_URL = None

load_dotenv(".env")
# config = dotenv_values(".env")


import commands as command
from commands import *


def file_hash(filename=__file__):
    """utils"""
    return sha1(str(os.stat(filename)).encode("utf8")).hexdigest()


def wh_url():
    """utils"""
    return (
        WEBHOOK_DOMAIN + (f":{WEBHOOK_PORT}" if bool(WEBHOOK_PORT) else "") + wh_path()
    )


def wh_path():
    """utils"""
    return "/bot"
    return (
        WEBHOOK_PATH
        + "/"
        + sha1(f"{FILE_TOKEN}:{TG_TOKEN}".encode("utf8")).hexdigest()
        + "/"
    )


def set_webhook():
    # A JSON-serialized list of the update types you want your bot to receive. For example, specify [“message”, “edited_channel_post”, “callback_query”] to only receive updates of these types. See Update for a complete list of available update types. Specify an empty list to receive all update types except chat_member (default). If not specified, the previous setting will be used.
    # https://core.telegram.org/bots/api#getting-updates
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

    # var_dump('set_webhook')

    global FILE_TOKEN, WEBHOOK_DOMAIN, WH_URL
    bot = command.bot

    # https://api.telegram.org/bot{TOKEN}/getWebhookInfo
    bot_nfo = bot.get_webhook_info()
    fh = file_hash()
    wh = wh_url()

    # var_dump(fh, wh, not (WH_URL != bot_nfo.url and FILE_TOKEN != fh))

    if not (WH_URL == bot_nfo.url and FILE_TOKEN == fh):
        FILE_TOKEN = fh
        WH_URL = wh

        bot.remove_webhook()

        #         set_webhook(
        #             token,
        #             url=None,
        #             certificate=None,
        #             max_connections=None,
        #             allowed_updates=None,
        #             ip_address=None,
        #             drop_pending_updates=None,
        #             timeout=None,
        #         ):

        bot.set_webhook(
            url=WH_URL,
            max_connections=TG_MAX_CONNECTION,
            allowed_updates=[],
            # allowed_updates=ALLOWED_UPDATES,
            # drop_pending_updates=TG_DROP_UPDATES,
            drop_pending_updates=True,
            timeout=TG_TIMEOUT,
        )

    log.debug(bot.get_webhook_info())

    return


FILE_TOKEN = file_hash()
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/bot")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", "")
WH_PATH = wh_path()
WH_URL = wh_url()


# Initialize with a Project Key
TG_TOKEN = os.getenv("TG_TOKEN", "#_#")
TG_MAX_CONNECTION = int(os.getenv("TG_MAX_CONNECTION", 40))
TG_DROP_UPDATES = bool(os.getenv("TG_DROP_UPDATES", None))
TG_TIMEOUT = int(os.getenv("TG_TIMEOUT", 10))
TG_PARSE_MODE = os.getenv("TG_PARSE_MODE", None)

deta = Deta(os.getenv("DETA_PROJECT_KEY"))
DETA_DB_NAME = os.getenv("DETA_DB_NAME", TG_TOKEN)
DB = deta.Base(DETA_DB_NAME)
SESSION_DB = deta.Base("SESSION")


# https://habr.com/ru/company/ods/blog/462141/
app = FastAPI()


# import utils as util
# from utils import *

####
##
# Begin
#

if os.getenv("TG_MODE") == "updates":
    bot.polling(none_stop=True, timeout=TG_TIMEOUT)
    # bot = telebot.TeleBot(TG_TOKEN, threaded=False, parse_mode=TG_PARSE_MODE)
    # bot = telebot.TeleBot(TG_TOKEN, parse_mode=TG_PARSE_MODE)
else:
    set_webhook()


# pylint: disable=unused-argument
@app.post(WH_PATH, response_class=Response, status_code=200)
async def webhook(
    request: Request,
    response: Response,
    # db: Session = Depends(get_db),    # get_db: interface yield
    payload: dict = Body(...),
):
    """process only requests with correct bot token"""

    # payload = json.loads( await request.body() )
    # message = payload['message']

    # var_dump('update_id' in payload)
    if "update_id" in payload:
        #   copypaste from bot.get_updates()
        data = [types.Update.de_json(ju) for ju in [payload]]
        # data - Object of type Update is not JSON serializable
        bot.process_new_updates(data)
        var_dump("bot.process_new_updates")

    else:
        if "cron" in payload:
            response.status_code = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
            #             bot.process_new_updates([])
            bot.process_new_messages([])
        else:
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    # return JSONResponse(
    #     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #     content={"detail": jsonable_encoder(payload)},
    # )

    return


@app.on_event("startup")
@app.get("/", response_class=HTMLResponse, status_code=403)
@app.get("/{param}", response_class=HTMLResponse, status_code=403)
@app.get("/{param}/", response_class=HTMLResponse, status_code=403)
async def docroot(param=""):  # pylint: disable=unused-argument
    """ default route """

    set_webhook()

    return f"And They Have a Plan : {FILE_TOKEN}"


def main():
    """Start here"""
    log.info("Start main()")
    log.debug(bot)

    import uvicorn

    uvicorn.run(app)

    if os.getenv("TG_MODE") == "webhook":
        set_webhook()
    else:
        bot.polling(none_stop=True, timeout=TG_TIMEOUT)

    sys.exit("Bot exited")


if __name__ == "__main__":

    main()
