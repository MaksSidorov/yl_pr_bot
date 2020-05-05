from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram_functions import *
from telegram.ext import Updater, MessageHandler, Filters

# Стартовая клавиатура
reply_keyboard_start = [['Найти фильм', 'Порекомендовать фильм'], ['Оценить фильм', 'Найти ближ. кинотеатр']]
markup_start = ReplyKeyboardMarkup(reply_keyboard_start, one_time_keyboard=True)


conv_handler = ConversationHandler(
    # Точка входа в диалог.
    # В данном случае — команда /start. Она задаёт первый вопрос.
    entry_points=[CommandHandler('start', start)],

    # Состояние внутри диалога.
    # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
    states={
        # Функция читает ответ на первый вопрос и задаёт второй.
        1: [MessageHandler(Filters.text, first_response)],
        # Функция читает ответ на второй вопрос и завершает диалог.
        2: [MessageHandler(Filters.text, sucs)]
    },

    # Точка прерывания диалога. В данном случае — команда /stop.
    fallbacks=[CommandHandler('stop', stop)]
)


if __name__ == '__main__':
    print('Файл с диалогами и клавиатурами')