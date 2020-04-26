from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, Bot
import requests
from kinopoisk_parse import *


# def start(update, context):
#     update.message.reply_text(
#         "Привет! Я кино-бот. Я помогу тебе выбрать фильм, чтобы "
#         "подробнее узнать о финциях напищите /help или нажмите кнопку 'Помощь'")





def film_info(update, context):
    inf = get_all_info(film_id=int(context.args[0]))
    update.message.reply_text(inf[0])
    context.bot.sendPhoto(chat_id=update.message.chat_id, photo=inf[1])




if __name__ == '__main__':
    pass
