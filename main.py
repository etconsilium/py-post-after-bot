#!/usr/bin/env python3
####
##
##
#
"""
module description
"""

# pylint:    disable=e0401
# pylint:    disable=c0112,c0116


# import time
# import requests
import os
import json
import telebot

from var_dump import var_dump
from dotenv import load_dotenv
from dotenv import dotenv_values
from hashlib import sha1
from urllib.parse import urlunparse
from urllib.parse import urljoin
from loguru import logger as log

# from tqdm import tqdm
from telebot import TeleBot
from telebot import apihelper
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from fastapi import FastAPI
from fastapi import Body
from fastapi import Request
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse

load_dotenv('.env')
config = dotenv_values('.env')

FILE_TOKEN = TG_TOKEN = WEBHOOK_DOMAIN = WEBHOOK_PATH = WEBHOOK_URL = None


def file_hash(filename=__file__):
    '''utils'''
    return sha1(str(os.stat(filename)).encode('utf8')).hexdigest()


def wh_url():
    '''utils'''
    # return '/bot'
    return (
        WEBHOOK_PATH
        + '/'
        + sha1(f"{FILE_TOKEN}:{TG_TOKEN}".encode('utf8')).hexdigest()
        + '/'
    )


FILE_TOKEN = file_hash()
TG_TOKEN = os.getenv("TG_TOKEN", ">_<`")
WEBHOOK_DOMAIN = os.getenv('WEBHOOK_DOMAIN', '')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/bot')
WEBHOOK_URL = wh_url()

# https://habr.com/ru/company/ods/blog/462141/
app = FastAPI()
# bot = telebot.TeleBot(TG_TOKEN)
bot = telebot.TeleBot(TG_TOKEN, threaded=False)
# bot.polling(none_stop=True, timeout=10)


def set_webhook():
    global FILE_TOKEN, WEBHOOK_DOMAIN, WEBHOOK_URL
    bot.remove_webhook()
    fh = file_hash()
    if FILE_TOKEN != fh:
        FILE_TOKEN = fh

    WEBHOOK_URL = wh_url()

    # def set_webhook(token, url=None, certificate=None, max_connections=None, allowed_updates=None, ip_address=None,
    #             drop_pending_updates = None, timeout=None):

    #
    # A JSON-serialized list of the update types you want your bot to receive. For example, specify [“message”, “edited_channel_post”, “callback_query”] to only receive updates of these types. See Update for a complete list of available update types. Specify an empty list to receive all update types except chat_member (default). If not specified, the previous setting will be used.
    # https://core.tlgr.org/bots/api#getting-updates
    #
    allowed_updates = [
        'message',
        'edited_message',
        'channel_post',
        'edited_channel_post',
        'inline_query',
        'chosen_inline_result',
        'callback_query',
        'shipping_query',
        'poll',
        'poll_answer',
        'my_chat_member',
        'chat_member',
    ]
    bot.set_webhook(
        url=f"{WEBHOOK_DOMAIN}:443{WEBHOOK_URL}",
        max_connections=40,
        timeout=10,
        allowed_updates=[],
        # allowed_updates=allowed_updates,
        # drop_pending_updates=bool(TG_DROP_UPDATES)
    )

    log.debug(bot.get_webhook_info())


@app.post(WEBHOOK_URL, response_class=Response, status_code=200)
# async def webhook(request: Request):  #   commonly variant yet
async def webhook(payload: dict = Body(...)):
    ''' process only requests with correct bot token'''

    #   copypaste from bot.get_updates()
    data = [types.Update.de_json(ju) for ju in [payload]]
    bot.process_new_updates(data)

    return


@app.get("/")
@app.on_event("startup")
async def docroot():
    """ default route """

    set_webhook()

    global FILE_TOKEN
    return "And They Have a Plan : " + FILE_TOKEN


# @app.get("/{param}")
# @app.get("/{param}/")
async def any(param=""):  # pylint: disable=unused-argument
    """ default route """
    return "And They Have a Plan : " + param


@bot.message_handler(commands=["help", "start"])
def welcome_message(message):
    bot.reply_to(message, "Hi there, I am EchoBot")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
@bot.message_handler(content_types=["text"])
def echo_message(message):
    # bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, message.text)


def main():
    """Start here"""
    log.info("Start main()")
    import uvicorn

    uvicorn.run(app)

    # bot.polling(none_stop=True, timeout=20)
    set_webhook()

    exit("Bot exited")


if __name__ == "__main__":
    # log.debug(config)
    log.info('start bot via main()')
    log.info(bot)

    log.warning(WEBHOOK_URL)

    main()
