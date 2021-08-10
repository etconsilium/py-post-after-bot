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
# import json
# import requests
import os
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

load_dotenv('.env')
config = dotenv_values('.env')

FILE_TOKEN = str(os.stat(__file__))
TG_TOKEN = os.getenv("TG_TOKEN", ">_<`")
WEBHOOK_DOMAIN = os.getenv('WEBHOOK_DOMAIN', '')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/bot')
WEBHOOK_URL = (
    WEBHOOK_PATH
    + '/'
    + sha1(f"{FILE_TOKEN}:{TG_TOKEN}".encode('utf8')).hexdigest()
    + '/'
)

log.debug(FILE_TOKEN)
log.debug(WEBHOOK_URL)

app = FastAPI()
bot = telebot.TeleBot(TG_TOKEN)

# @app.post("/{token}/")
@app.post(WEBHOOK_URL)
async def webhook(data):
    ''' process only requests with correct bot token'''
    log.info(data)
    return app.response(200)

    if request.match_info.get("token") == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        status = 200
    else:
        status = 403

    return app.response(status)


@app.get("/")
async def docroot():
    """ default route """
    if FILE_TOKEN != str(os.stat(__file__)):
        FILE_TOKEN = str(os.stat(__file__))
        set_webhook()

    return "And They Have a Plan"


@app.get("/{param}")
@app.get("/{param}/")
async def any(param=""):  # pylint: disable=unused-argument
    """ default route """
    return "And They Have a Plan : " + param


@bot.message_handler(commands=["start", "help"])
def hello_chat(message):
    """"""
    bot.send_message(message.chat.id, "Hello Chat!")
    if message.from_user.first_name is not None:
        bot.reply_to(message, f"Hi here, {message.from_user.first_name}!")


@bot.message_handler(commands=["picture", "pic"])
def send_picture(message):
    """"""
    bot.reply_to(message, f"picture in chat_id#{message.chat.id}")
    bot.send_photo(
        message.chat.id,
        open("./data/pic.jpg", "rb"),
        "картинку (как картинку) с подписью",
    )


@bot.message_handler(commands=["video", "vid"])
def send_video(message):
    """"""
    bot.reply_to(message, "its really MP4")
    bot.send_video(message.chat.id, open("./data/vid.mp4", "rb"), "but...")


@bot.message_handler(commands=["pdf"])
def send_pdf(message):
    """"""
    bot.reply_to(message, "PDF NOW!")
    bot.send_document(message.chat.id, open("./data/pdf.pdf", "rb"))


def set_webhook():
    bot.delete_webhook()
    log.warning(f"{WEBHOOK_DOMAIN}{WEBHOOK_URL}")
    # def set_webhook(token, url=None, certificate=None, max_connections=None, allowed_updates=None, ip_address=None,
    #             drop_pending_updates = None, timeout=None):
    bot.set_webhook(
        url=f"{WEBHOOK_DOMAIN}{WEBHOOK_URL}", allowed_updates=True, timeout=30
    )
    log.debug(bot.get_webhook_info())


def main():
    """Start here"""
    log.info("Start main()")
    import uvicorn

    uvicorn.run(app)

    # bot.polling(none_stop=True, timeout=20)
    bot.set_webhook()

    exit("Bot exited")


if __name__ == "__main__":

    log.debug(config)
    log.info('bot')
    log.info(bot)

    log.debug(TG_TOKEN)
    log.warning(WEBHOOK_URL)

    main()
