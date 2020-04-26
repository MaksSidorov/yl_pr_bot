from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove, InlineKeyboardButton
import socks
import socket

from telegram_functions import *

reply_keyboard1 = [['Адресс']]
markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=False)
reply_keyboard2 = [['df']]
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=False)


def start(update, context):
    update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?",
        reply_markup=markup1
    )


def help(update, context):
    update.message.reply_text(
        "Я пока не умею помогать... Я только ваше эхо.")


def address(update, context):
    update.message.reply_text(
        "Адрес: г. Москва, ул. Льва Толстого, 16")


def phone(update, context):
    update.message.reply_text("Телефон: +7(495)776-3030")


def site(update, context):
    update.message.reply_text(
        "Сайт: http://www.yandex.ru/company")


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


# Зарегистрируем их в диспетчере.

socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
socket.socket = socks.socksocket

TOKEN = '1220774917:AAFn0XURWj2_sh5u0srJeukLB5SMOP1kQEY'


def echo(update, context):
    # У объекта класса Updater есть поле message,
    # являющееся объектом сообщения.
    # У message есть поле text, содержащее текст полученного сообщения,
    # а также метод reply_text(str),
    # отсылающий ответ пользователю, от которого получено сообщение.
    update.message.reply_text(
        "Ok",
        reply_markup=markup2
    )


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("film_info", film_info))
    dp.add_handler(CommandHandler("address", address))
    dp.add_handler(CommandHandler("phone", phone))
    dp.add_handler(CommandHandler("site", site))
    dp.add_handler(CommandHandler("work_time", help))
    dp.add_handler(CommandHandler("close", close_keyboard))
    text_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(text_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
