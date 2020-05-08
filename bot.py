from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext
import socks
import socket
from telegram_functions import *

# Подключение через Тор браузер
socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
socket.socket = socks.socksocket

TOKEN = '1220774917:AAFn0XURWj2_sh5u0srJeukLB5SMOP1kQEY'


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
