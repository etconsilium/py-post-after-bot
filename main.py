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
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse

load_dotenv('.env')
config = dotenv_values('.env')

FILE_TOKEN = TG_TOKEN = WEBHOOK_DOMAIN = WEBHOOK_PATH = WEBHOOK_URL = None

ALLOWED_UPDATES = [
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


def file_hash(filename=__file__):
    '''utils'''
    return sha1(str(os.stat(filename)).encode('utf8')).hexdigest()


def wh_url():
    '''utils'''
    # return '/bot'
    return (
        WEBHOOK_DOMAIN + (f":{WEBHOOK_PORT}" if bool(WEBHOOK_PORT) else '') + wh_path()
    )


def wh_path():
    '''utils'''
    return (
        WEBHOOK_PATH
        + '/'
        + sha1(f"{FILE_TOKEN}:{TG_TOKEN}".encode('utf8')).hexdigest()
        + '/'
    )


FILE_TOKEN = file_hash()
TG_TOKEN = os.getenv("TG_TOKEN", "#_#")
TG_MAX_CONNECTION = int(os.getenv("TG_MAX_CONNECTION", 40))
TG_DROP_UPDATES = bool(os.getenv("TG_DROP_UPDATES", None))
TG_TIMEOUT = int(os.getenv("TG_TIMEOUT", 10))

WEBHOOK_DOMAIN = os.getenv('WEBHOOK_DOMAIN', '')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/bot')
WEBHOOK_PORT = os.getenv('WEBHOOK_PORT', '')
WH_PATH = wh_path()
WH_URL = wh_url()

# https://habr.com/ru/company/ods/blog/462141/
app = FastAPI()
bot = telebot.TeleBot(
    TG_TOKEN, threaded=False, parse_mode=os.getenv("TG_PARSE_MODE", None)
)
# bot.polling(none_stop=True, timeout=10)


def set_webhook():
    global FILE_TOKEN, WEBHOOK_DOMAIN, WH_URL
    bot.remove_webhook()
    fh = file_hash()
    if FILE_TOKEN != fh:
        FILE_TOKEN = fh

    WH_URL = wh_url()

    # def set_webhook(token, url=None, certificate=None, max_connections=None, allowed_updates=None, ip_address=None,
    #             drop_pending_updates = None, timeout=None):

    #
    # A JSON-serialized list of the update types you want your bot to receive. For example, specify [“message”, “edited_channel_post”, “callback_query”] to only receive updates of these types. See Update for a complete list of available update types. Specify an empty list to receive all update types except chat_member (default). If not specified, the previous setting will be used.
    # https://core.tlgr.org/bots/api#getting-updates
    #
    bot.set_webhook(
        url=WH_URL,
        max_connections=TG_MAX_CONNECTION,
        timeout=TG_TIMEOUT,
        allowed_updates=[],
        # allowed_updates=ALLOWED_UPDATES,
        drop_pending_updates=TG_DROP_UPDATES,
    )

    log.debug(bot.get_webhook_info())


# pylint: disable=unused-argument
@app.post(WH_PATH, response_class=Response, status_code=200)
async def webhook(request: Request, response: Response, payload: dict = Body(...)):
    ''' process only requests with correct bot token'''

    # payload = json.loads( await request.body() )

    # if (not bool(payload)) and hasattr(payload, 'update_id'):
    if 'update_id' in payload:
        #   copypaste from bot.get_updates()
        data = [types.Update.de_json(ju) for ju in [payload]]
        bot.process_new_updates(data)

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

    global FILE_TOKEN

    return f"And They Have a Plan : {FILE_TOKEN}"


BEEP_STATUS = None


@bot.message_handler(commands=["start"])
def start_command(message: types.Update):
    print("start here")

    t = message.entities[0]
    if len(message.text) > t.length:
        # bot.send_message(message.chat.id, 'start abonent box')
        BEEP_STATUS = 1
        start_beep(message)
    else:
        # bot.send_message(message.chat.id, 'start text')
        welcome_message(message)
    return


@bot.message_handler(commands=["help"])
def help_command(message: types.Update):
    text = """
/beep - [секретик] : записать приветственное сообщение
/start - секретик : отправить сообщение абоненту 
/beep - beep (два раза) : прочитать сообщения
/check - проверить сообщения (как два бип)
/source - sourcecode
/help - список команд

/beep - [секретик] [Привет!] записать приветственное сообщение
/beepbeep - прочитать сообщения
/check - проверить сообщения
/source - показать исходный код (для разработчиков)
/help - список команд
"""
    bot.send_message(message.chat.id, text)
    # bot.reply_to(message, message.text)
    return


@bot.message_handler(commands=["beep"])
def beep_command(message: types.Update):

    beep = 'beep'

    return


@bot.message_handler(commands=["check"])
def check_command(message: types.Update):

    echo_message(message)

    return


@bot.message_handler(commands=["source"])
def source_command(message: types.Update):
    # bot.reply_to(message, '<pre>' + open(__file__, "rb") + '</pre>')

    from pathlib import Path

    MAX_LENGHT = 4096
    # MAX_LENGHT = 8192
    # r = '<pre>' + Path(__file__).read_text() + '</pre>'
    r = Path(__file__).read_text()
    if len(r) > MAX_LENGHT:
        for x in range(0, len(r), MAX_LENGHT):
            bot.send_message(
                message.chat.id,
                '<pre><code>{}</code></pre>'.format(r[x : x + MAX_LENGHT]),
                parse_mode=None,
            )

    return


@bot.message_handler(commands=["beep"])
def start_beep(message: types.Update):

    global BEEP_STATUS
    beep = 'Beep'

    t = message.entities[0]

    if len(message.text) > t.length:

        BEEP_STATUS = 2 if 1 == BEEP_STATUS else 1

        abonent_box = (message.text[t.offset + t.length :]).strip()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttonB = types.KeyboardButton(f'/{beep}!')
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
        f"Hi there, You have reached the postponement machine with a combination <a href='https://t.me/post_after_bot?start={abonent_box}'><b>{abonent_box.upper()}</b></a>. "
        + f" Post a message after the {beep}!"
        + os.linesep * 2
        + f"Нажмите кнопку и напишите сообщение для абонента с кодовым именем <a href='https://t.me/post_after_bot?start={abonent_box}'><b>{abonent_box.upper()}</b></a>"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

    return


@bot.message_handler(content_types=["text"])
def echo_message(message: types.Update):
    # bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, message.text)
    return


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def welcome_message(message: types.Update):
    # bot.reply_to(message, message.text)
    # bot.send_message(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'welcome')
    return


def main():
    """Start here"""
    log.info("Start main()")
    import uvicorn

    uvicorn.run(app)

    if os.getenv('TG_MODE') == 'webhook':
        set_webhook()
    else:
        bot.polling(none_stop=True, timeout=TG_TIMEOUT)

    exit("Bot exited")


if __name__ == "__main__":
    # log.debug(config)
    log.info('start bot via main()')
    log.info(bot)

    main()
