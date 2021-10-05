####
##
#
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
from db import id as row_id, message_id, key as row_key
from db import hasher
from db import dateparser, strdateparser

from models import Record, Message
from session import Session

import settings as sets
from settings import CRLF


# bot = telebot.TeleBot(TG_TOKEN, threaded=False, parse_mode=TG_PARSE_MODE)
bot = telebot.TeleBot(sets.TG_TOKEN, parse_mode=sets.TG_PARSE_MODE)

# abot = telebot.AsyncTeleBot("TOKEN")
# res = abot.send_message(cid, f"text")
# try:
#     result = res.wait()
#     print(result.message_id)
# except Exception as e:
#     print(e)

# BEEP_BIG_BUTTON =
BBB = "Beep"

HELP_TEXT = """\
/beep - [код] : записать приветственное сообщение
/start - [код] : отправить сообщение абоненту 
/check - проверить сообщения (как два бип)
/source - sourcecode
/help - список команд
"""
# /beep - beep (два раза) : прочитать свои сообщения


def abonent_href(abonent_box: str):
    """pattern"""
    """
    allowed html tags
    <b>bold</b>, <strong>bold</strong> <i>italic</i>, <em>italic</em> <a href="URL">inline URL</a>
    <code>inline fixed-width code</code> <pre>pre-formatted fixed-width code block</pre>
    """
    return f"<a href='https://t.me/post_after_bot?start={abonent_box}'><b>{abonent_box.upper()}</b></a>"


def abonent_box(message):
    t = message.entities[0]
    return (message.text[t.offset + t.length :]).strip()


def beep_markup_menu(message):

    markup = None
    if bool(abonent_box):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button = types.KeyboardButton(f"/{BBB}!")
        markup.row(button)

    return markup


def check_status(message):
    return True


def echo_message(message: types.Update, text: str = None):
    # bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, message.text if text is None else text)


def start_message(message):
    href = abonent_href(abonent_box(message))
    markup = beep_markup_menu(message)
    text = (
        f"Hi there, You have reached the postponement machine with a combination"
        + f" {href}. Post message and press /{BBB} button, message send after {BBB}!"
        + CRLF * 2
        + f"Отправьте сообщение для абонента {href} и нажмите кнопку {BBB}."
        + " Ваше сообщение будет отослано после подтверждения"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)


def welcome_message(message):
    # bot.send_message(message.chat.id, message.text)
    bot.send_message(message.chat.id, "> к работе готов <")


@bot.message_handler(commands=["start"])
def start_command(message):
    session = Session.one(message_id(message))
    ab = abonent_box(message)

    # @TODO решить апдейтом
    session.last_command = message.text
    session.abonent = ab
    session.step = ""

    if bool(ab):
        session.step = "READY_TO_RECORD"

        # start_message(message)
        href = abonent_href(abonent_box(message))
        markup = beep_markup_menu(message)
        text = (
            f"Hi there, You have reached the postponement machine with a combination"
            + f" {href}. Post message and press /{BBB} button, message send after {BBB}!"
            + (CRLF * 2)
            + f"Отправьте сообщение для абонента {href} и нажмите кнопку {BBB}."
            + " Ваше сообщение будет отослано после подтверждения"
        )
        bot.send_message(message.chat.id, text, reply_markup=markup)

    else:
        # welcome_message(message)
        bot.send_message(message.chat.id, "> к работе готов <")

    # echo_message(message, 'start command')
    session.insert()


@bot.message_handler(commands=["beep", BBB])
def beep_command(message):
    session = Session.one(message_id(message))

    # делаем иллюзию интерактивного меню
    bot.delete_message(message.chat.id, message.id)

    # bot.send_message(
    #     message.chat.id,
    #     "text: %s \n session: \n%s" % ("READY_TO_RECORD" == session.step, str(session)),
    # )

    # if (
    #     session.last_command.lower().startswith("/start")
    #     and "READY_TO_RECORD" == session.step
    # ):
    if "READY_TO_RECORD" == session.step:
        # bot.send_message(message.chat.id, "BEEP COMMAND")
        # do
        # Message(
        r = Record(
            {
                "abonent": session.abonent,
                "content": session.message,
                "from_id": message.from_user.id,
                "to_id": None,
                "status": "MESSAGE_SENDED",
            }
        ).insert()
        # echo_message(message, str(r))
        echo_message(message, "Сообщение <pre>%s</pre> отправлено получателю" % (r.key))
        session.step = ""
        session.last_command = message.text
        pass

    elif session.last_command.startswith(BBB) and not (session.step):
        session.last_command = None
        session.step = BBB
        # & clear_all
        pass
    else:
        session.last_command = message.text
        session.step = BBB

    # echo_message(message, "beep command")
    session.insert()


@bot.message_handler(commands=["check"])
def check_command(message):
    echo_message(message)


@bot.message_handler(commands=["help"])
def help_command(message: types.Update):
    bot.send_message(message.chat.id, HELP_TEXT)
    # bot.reply_to(message, message.text)


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


@bot.message_handler(content_types=["text"])
def text_handler(message: types.Update):
    if message.text.startswith(f"/{BBB}"):  #   кнопка не команда ¯\_(ツ)_/¯
        return beep_command(message)

    session = Session.one(message_id(message))
    # bot.reply_to(message, message.text)
    # bot.send_message(
    #     message.chat.id,
    #     "text: %s \n session: \n%s"
    #     % (message.text.startswith(f"/{BBB}"), str(session)),
    # )

    if (
        session.last_command.lower().startswith("/start")
        and "READY_TO_RECORD" == session.step
    ):
        session.message = message.text

        bot.reply_to(
            message,
            f"Подтвердите отправку кнопкой /{BBB}. Confirm sending!{CRLF}(or type new)",
        )

    echo_message(message, message.text)
    session.insert()


# any message
# @bot.message_handler(func=lambda message: True)
# @bot.message_handler(content_types=["text"])
def default_handler(message):
    bot.reply_to(message, message.text)


# @bot.message_handler(commands=["beep"])
def DELME_start_beep(message):
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
