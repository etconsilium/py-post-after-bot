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

import telebot
from telebot import TeleBot
from telebot import apihelper
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import db

# from db import id as row_id, message_id, key as row_key
from db import hasher

from models import Record
from session import Session

import settings as sets


# bot = telebot.TeleBot(TG_TOKEN, threaded=False, parse_mode=TG_PARSE_MODE)
bot = telebot.TeleBot(sets.TG_TOKEN, parse_mode=sets.TG_PARSE_MODE)

# abot = telebot.AsyncTeleBot("TOKEN")
# res = abot.send_message(cid, f"text")
# try:
#     result = res.wait()
#     print(result.message_id)
# except Exception as e:
#     print(e)


@bot.message_handler(commands=["start"])
def start_command(message: types.Update):

    key = db.key(message)
    print(key)
    session = Session.one(key)
    session.command = message.text
    print(session)

    echo_message(message, "%s -=-=-=-=- %s" % (session.command, str(session)))

    t = message.entities[0]
    if len(message.text) > t.length:
        BEEP_STATUS = 1
        #         send_start_plus_key(message)
        echo_message(message, "send_start_plus_key")
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
    Record.one(db.message_id(message))

    echo_message(message)
    return


@bot.message_handler(commands=["beep"])
def start_beep(message: types.Update):
    global BEEP_STATUS

    beep = "Beep"
    t = message.entities[0]
    abonent_box = (message.text[t.offset + t.length :]).strip()
    href = "<a href='https://t.me/post_after_bot?start={abonent_box}'><b>{abonent_box.upper()}</b></a>"

    print(message.text, abonent_box)
    print(bool(abonent_box))
    print(len(message.text) > t.length and bool(abonent_box))

    if len(message.text) > t.length and bool(abonent_box):
        # :mailing: FetchResponse
        mailing = Record.find({"abonent_box?eq": abonent_box})
        print("mailing", mailing)
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
def echo_message(message: types.Update, text: str = None):
    # bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, message.text if text is None else text)
    return


def send_start_plus_key(message: types.Update):
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
