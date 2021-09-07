####
##
#
"""
Bot's commands
"""


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


import telebot
from telebot import TeleBot
from telebot import apihelper
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db import db_hash

load_dotenv(".env")
# config = dotenv_values(".env")

import db
from db import DB
from db import db_hash

# Initialize with a Project Key
TG_TOKEN = os.getenv("TG_TOKEN", "#_#")
TG_MAX_CONNECTION = int(os.getenv("TG_MAX_CONNECTION", "40"))
TG_DROP_UPDATES = bool(os.getenv("TG_DROP_UPDATES", None))
TG_TIMEOUT = int(os.getenv("TG_TIMEOUT", "10"))
TG_PARSE_MODE = os.getenv("TG_PARSE_MODE", None)

# bot = telebot.TeleBot(TG_TOKEN, threaded=False, parse_mode=TG_PARSE_MODE)
bot = telebot.TeleBot(TG_TOKEN, parse_mode=TG_PARSE_MODE)

# abot = telebot.AsyncTeleBot("TOKEN")
# res = abot.send_message(cid, f"text")
# try:
#     result = res.wait()
#     print(result.message_id)
# except Exception as e:
#     print(e)


@bot.message_handler(commands=["start"])
def start_command(message: types.Update):

    key = db_hash(message)
    session = DB.get(key)

    t = message.entities[0]
    if len(message.text) > t.length:
        BEEP_STATUS = 1
        write_message_1(message)
    else:
        # bot.send_message(message.chat.id, 'start text')
        welcome_message(message)
    return


@bot.message_handler(commands=["beep"])
def beep_command(message: types.Update):
    global BEEP_STATUS
    beep = "beep"
    echo_message(message)
    return


@bot.message_handler(commands=["check"])
def check_command(message: types.Update):
    DB.get(key)

    echo_message(message)
    return


@bot.message_handler(commands=["beep"])
def start_beep(message: types.Update):
    global BEEP_STATUS, DB

    beep = "Beep"
    t = message.entities[0]
    abonent_box = (message.text[t.offset + t.length :]).strip()
    href = "<a href='https://t.me/post_after_bot?start={abonent_box}'><b>{abonent_box.upper()}</b></a>"

    var_dump(message.text, abonent_box)
    var_dump(bool(abonent_box))
    var_dump(len(message.text) > t.length and bool(abonent_box))

    return

    if len(message.text) > t.length and bool(abonent_box):
        # :mailing: FetchResponse
        mailing = DB.fetch({"abonent_box?eq": abonent_box})
        var_dump("mailing", mailing)
        BEEP_STATUS = 2 if 1 == BEEP_STATUS else 1

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttonB = types.KeyboardButton(f"/{beep}!")
    markup.row(buttonB)

    # InlineKeyboardButton(text, url=None, callback_data=None, switch_inline_query=None, switch_inline_query_current_chat=None, callback_game=None, pay=None, login_url=None, **_kwargs)
    # markup = types.InlineKeyboardMarkup()
    # buttonB = types.InlineKeyboardButton('Beep!')
    # markup.row(buttonB)

    # user_id = message.from.id
    chat_id = message.chat.id

    """
    allowed html tags
    <b>bold</b>, <strong>bold</strong> <i>italic</i>, <em>italic</em> <a href="URL">inline URL</a>
    <code>inline fixed-width code</code> <pre>pre-formatted fixed-width code block</pre>
    """
    text = (
        f"Hi there, You have reached the postponement machine with a combination"
        + f" {href}. Post a message after the {beep}!"
        + os.linesep * 2
        + f"Нажмите кнопку и напишите сообщение на абонентский ящик {href}"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

    return


@bot.message_handler(commands=["help"])
def help_command(message: types.Update):
    text = """\
/beep - [код] : записать приветственное сообщение
/start - [код] : отправить сообщение абоненту 
/beep - beep (два раза) : прочитать сообщения
/check - проверить сообщения (как два бип)
/source - sourcecode
/help - список команд
"""
    bot.send_message(message.chat.id, text)
    # bot.reply_to(message, message.text)
    return


@bot.message_handler(commands=["source"])
def source_command(message: types.Update):
    # bot.reply_to(message, '<pre>' + open(__file__, "rb") + '</pre>')

    from pathlib import Path

    MAX_LENGHT = 4096
    # MAX_LENGHT = 8192
    # r = '<pre>' + Path(__file__).read_text() + '</pre>'
    #     r = Path(__file__).read_text()
    r = Path("main.py").read_text()
    if len(r) > MAX_LENGHT:
        for x in range(0, len(r), MAX_LENGHT):
            bot.send_message(
                message.chat.id,
                "<pre><code>{}</code></pre>".format(r[x : x + MAX_LENGHT]),
                parse_mode=None,
            )

    return


@bot.message_handler(content_types=["text"])
def echo_message(message: types.Update):
    # bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, message.text)
    return


def write_message_1(message: types.Update):
    beep = "Beep"
    t = message.entities[0]
    abonent_box = (message.text[t.offset + t.length :]).strip()
    href = f"<a href='https://t.me/post_after_bot?start={abonent_box}'><b>{abonent_box.upper()}</b></a>"
    #     var_dump(abonent_box, href)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button = types.KeyboardButton(f"/{beep}!")
    markup.row(button)

    # InlineKeyboardButton(text, url=None, callback_data=None, switch_inline_query=None, switch_inline_query_current_chat=None, callback_game=None, pay=None, login_url=None, **_kwargs)
    # markup = types.InlineKeyboardMarkup()
    # buttonB = types.InlineKeyboardButton('Beep!')
    # markup.row(buttonB)

    #     user_id = message.from_user.id
    #     chat_id = message.chat.id

    """
    allowed html tags
    <b>bold</b>, <strong>bold</strong> <i>italic</i>, <em>italic</em> <a href="URL">inline URL</a>
    <code>inline fixed-width code</code> <pre>pre-formatted fixed-width code block</pre>
    """
    text = (
        f"Hi there, You have reached the postponement machine with a combination"
        + f" {href}. Post a message after the {beep}!"
        + os.linesep * 2
        + f"Нажмите кнопку {beep} и после этого отправльте сообщение абоненту {href}"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

    return


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# def welcome_message(message: types.Update):
def welcome_message(message):
    # bot.reply_to(message, message.text)
    # bot.send_message(message.chat.id, message.text)
    bot.send_message(message.chat.id, "welcome")
    return


# @bot.message_handler(func=lambda message: message.entities[0].type == "bot_command")
# def echo_command(message: types.Update):
def echo_command(message):
    bot.send_message(message.chat.id, "this is bot_command33")
    return
