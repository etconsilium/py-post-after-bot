#!/usr/bin/env python3
####
##
#
#
"""
телеграмный бот
 * автоответчик: сохраняет и показывает сообщения
 * анонимизатор: первоначальная идея

код иллюстрирует, как не надо писать код
также содержит примеры вариантов реализации (в комментариях)
  и хаков, которые описаны в документации, но их применение недостаточно ясно
"""

# pylint:    disable=e0401
# pylint:    disable=c0112,c0116

# import time
# import requests
import os
from os import environ
import sys
import json

from loguru import logger as log
from var_dump import var_dump

import settings as sets
from settings import sha
from settings import (
    TG_TOKEN,
    TG_MODE,
    TG_MAX_CONNECTION,
    TG_DROP_UPDATES,
    TG_PARSE_MODE,
    TG_TIMEOUT,
)

from commands import bot
import commands

from fastapi import FastAPI
from fastapi import Body
from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse


FILE_TOKEN = WEBHOOK_DOMAIN = WEBHOOK_PATH = WH_URL = WH_PATH = None

# https://habr.com/ru/company/ods/blog/462141/
app = FastAPI()


def file_hash(filename=__file__):
    """utils"""
    return sha(str(os.stat(filename)).encode("utf8")).hexdigest()


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
        + sha("{}:{}".format(FILE_TOKEN, TG_TOKEN).encode("utf8")).hexdigest()
        + "/"
    )


@app.on_event("startup")  # не на всех версиях работает
def set_webhook():

    global FILE_TOKEN, WEBHOOK_DOMAIN, WH_URL

    # https://api.telegram.org/bot{TOKEN}/getWebhookInfo
    bot_nfo = bot.get_webhook_info()
    fh = file_hash()
    wh = wh_url()

    var_dump(fh, wh, bot_nfo, not (WH_URL == bot_nfo.url and FILE_TOKEN == fh))

    if WH_URL != bot_nfo.url or FILE_TOKEN != fh:
        FILE_TOKEN = fh
        WH_URL = wh

        bot.remove_webhook()

        if "webhook" == TG_MODE:
            # Marvin's Marvellous Guide to All Things Webhook
            # https://core.telegram.org/bots/webhooks#the-short-version
            # https://core.telegram.org/bots/webhooks#testing-your-bot-with-updates

            bot.set_webhook(
                url=WH_URL,
                # certificate=None,
                max_connections=TG_MAX_CONNECTION,
                allowed_updates=[],
                # allowed_updates=ALLOWED_UPDATES,
                # ip_address=None,
                # drop_pending_updates=TG_DROP_UPDATES,
                drop_pending_updates=TG_DROP_UPDATES,
                # so it should wait as long as the maximum script execution time
                # timeout=TG_TIMEOUT,
            )
        else:
            bot.polling(
                none_stop=True,
                max_connections=TG_MAX_CONNECTION,
                drop_pending_updates=TG_DROP_UPDATES,
                timeout=TG_TIMEOUT,
            )
            # bot = telebot.TeleBot(TG_TOKEN, threaded=False, parse_mode=TG_PARSE_MODE)

    log.debug(bot.get_webhook_info())

    return


FILE_TOKEN = file_hash()
WEBHOOK_DOMAIN = environ.get("WEBHOOK_DOMAIN", "")
WEBHOOK_PATH = environ.get("WEBHOOK_PATH", "/bot")
WEBHOOK_PORT = environ.get("WEBHOOK_PORT", "")
WH_PATH = wh_path()
WH_URL = wh_url()


####
##
# Begin
#

# set_webhook()

# pylint: disable=unused-argument
@app.post(WH_PATH, response_class=JSONResponse, status_code=200)
async def webhook(
    request: Request,
    response: Response,
    # db: Session = Depends(get_db),    # get_db: interface yield
    payload: dict = Body(...),
):
    """process only requests with correct bot token"""

    from telebot import types

    # payload = json.loads( await request.body() )
    # message = payload['message']

    if "update_id" in payload:
        #   copypaste from bot.get_updates()
        data = [types.Update.de_json(ju) for ju in [payload]]
        # data - Object of type Update is not JSON serializable
        var_dump("bot.process_new_updates")
        var_dump(TG_MAX_CONNECTION)
        # var_dump(data)

        bot.process_new_updates(data)
        response.status_code = 200

    else:
        if "cron" in payload:
            response.status_code = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
            bot.process_new_messages([])  # push the queue
        else:
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    # return JSONResponse(
    #     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #     content={"detail": jsonable_encoder(payload)},
    # )

    return {"ok": True}


@app.get("/", response_class=HTMLResponse, status_code=403)
@app.get("/{param}", response_class=HTMLResponse, status_code=403)
async def docroot(param=""):  # pylint: disable=unused-argument
    """default route"""
    set_webhook()
    return f"And They Have a Plan : {FILE_TOKEN}"


def main():
    """Start here"""
    import uvicorn

    #     log.info("Start main()")
    #     log.debug(bot)

    uvicorn.run(app)

    sys.exit("Bot exited")


if __name__ == "__main__":

    main()
