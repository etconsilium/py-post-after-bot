#!/usr/bin/env python3
####
##
##
#
"""
module description
"""

# pylint:    disable=R
# pylint:    disable=unused-import

# import os
# import time
# import json
# import os
# import requests
import telebot

from var_dump import var_dump
from dotenv_config import Config

# from tqdm import tqdm
from loguru import logger as log
from telebot import TeleBot
from telebot import apihelper
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from fastapi import FastAPI

app = FastAPI()


config = Config(".env")
tg_token = config("TOKEN")
bot = telebot.TeleBot(tg_token)


@app.get("/")
@app.get("/{param}")
async def docroot(param=""):  # pylint: disable=unused-argument
    """ default route """
    return "And They Have a Plan"


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
    """"""
    if config("WEBHOOK_URL"):
        wh_url = "{}:{}{}".format(
            config("WEBHOOK_URL"), config("WEBHOOK_PORT"), config("WEBHOOK_PATH")
        )
        bot.remove_webhook()
        bot.set_webhook(url=wh_url)


def main():
    """Start here"""
    log.debug("Start here")

    bot.polling(none_stop=True, timeout=20)
    #    set_webhook()

    exit("Bot exited")


if __name__ == "__main__":
    main()
