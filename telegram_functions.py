from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import requests
from kinopoisk_parse import *
from data import db_session, user_rating


# Функции
def start(update, context):
    update.message.reply_text(
        "Привет! Я кино-бот. Я помогу тебе выбрать фильм, что вы хотите?", reply_markup=markup_start)

    return 1


def stop(update, context):
    update.message.reply_text(
        "Пока", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def first_response(update, context):
    resp = update.message.text
    if resp == 'Найти фильм':
        update.message.reply_text('Как называется фильм, который вам интересен?', reply_markup=ReplyKeyboardRemove())
        return 2
    elif resp == 'Порекомендовать фильм':
        update.message.reply_text('Выберите анр', reply_markup=markup_film_recom)
        return 7
    else:
        return ConversationHandler.END


def find_film(update, context):
    title = update.message.text
    res = kp_film_find(title.lower())
    context.user_data['res'] = res
    update.message.reply_text(
        "Какой из этих фильмов ваш? \n" + "\n".join(res[0]), reply_markup=markup_choose)

    return 3


def film_info(update, context):
    film_ch = update.message.text
    context.user_data['film_id'] = context.user_data['res'][1][int(film_ch) - 1]
    context.user_data['film_title'] = context.user_data['res'][0][int(film_ch) - 1]
    inf = get_all_info(film_id=context.user_data['film_id'])
    update.message.reply_text(inf[0], reply_markup=markup_film1)
    context.bot.sendPhoto(chat_id=update.message.chat_id, photo=inf[1])

    return 5


def second_response(update, context):
    resp = update.message.text
    if resp == 'В главное меню':
        update.message.reply_text('На главную',
                                  reply_markup=markup_menu)
        return 4
    elif resp == 'Посмотреть отзывы':
        inf = get_reviews(film_id=context.user_data['film_id'])
        update.message.reply_text(inf[0], reply_markup=markup_menu)
        update.message.reply_text(inf[1])
        return 4
    elif resp == 'Поставить оценку':
        update.message.reply_text(
            'Поставте оценку(Если оценка не будет от 0 до 10 или неправильный тип, оценка будет равна 10)',
            reply_markup=markup_rating)

        return 6


def put_rating(update, context):
    rating = update.message.text
    try:
        float_rating = float(rating)
    except TypeError as E:
        float_rating = 0.0
    if float_rating > 10 or float_rating < 0:
        float_rating = 0.0
    db_session.global_init("db/kinobot_data.sqlite")
    user_r = user_rating.UserRating()
    user_r.film_id = context.user_data['film_id']
    user_r.title = context.user_data['film_title'][3:]
    user_r.user_id = update.message.from_user.id
    user_r.us_rating = float_rating
    session = db_session.create_session()
    session.query(user_rating.UserRating).filter(user_rating.UserRating.film_id == context.user_data['film_id'],
                                                 user_rating.UserRating.user_id == update.message.from_user.id).delete()
    session.commit()
    session.add(user_r)
    session.commit()
    update.message.reply_text(
        'Вы поставили оценку {}'.format(float_rating), reply_markup=markup_menu)

    return 4


def choose_genre(update, context):
    genre = update.message.text.lower()
    db_session.global_init("db/kinobot_data.sqlite")
    session = db_session.create_session()
    print(221)
    if genre == 'любой':
        films_list = session.query(films.Film).order_by(films.Film.rating.desc()).all()
    else:
        films_list = session.query(films.Film).filter(
            films.Film.main_genre == genre).order_by(
            films.Film.rating.desc()).all()
    c = 0
    filmss = []
    print(films_list[0])
    for film in films_list:
        f = session.query(user_rating.UserRating).filter(user_rating.UserRating.film_id == film.film_id,
                                                         user_rating.UserRating.user_id == update.message.from_user.id).all()

        if len(f) == 0:
            c += 1
            filmss.append(film)
        print(c)
        if c >= 3:
            break
    print(filmss)
    update.message.reply_text(
        "Какой фильм выберите \n1. {} - {} \n2. {} - {} \n3. {} - {}".format(filmss[0].title, filmss[0].rating,
                                                                             filmss[1].title,
                                                                             filmss[0].rating, filmss[1].title,
                                                                             filmss[2].rating),
        reply_markup=markup_choose)
    context.user_data['res'] = [[filmss[0].title, filmss[1].title, filmss[2].title],
                                [filmss[0].film_id, filmss[1].film_id, filmss[2].film_id]]

    return 3


# Клавиатуры
reply_keyboard_start = [['Найти фильм', 'Порекомендовать фильм'],
                        [KeyboardButton(text='Найти ближ. кинотеатр', request_location=True)]]
markup_start = ReplyKeyboardMarkup(reply_keyboard_start, one_time_keyboard=True)

reply_keyboard_choose = [['1', '2', '3'], ['Нету']]
markup_choose = ReplyKeyboardMarkup(reply_keyboard_choose, one_time_keyboard=True)

reply_keyboard_film1 = [['Посмотреть отзывы', 'Поставить оценку', 'В главное меню']]
markup_film1 = ReplyKeyboardMarkup(reply_keyboard_film1, one_time_keyboard=True)

reply_keyboard_rating = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['10', '0'], ]
markup_rating = ReplyKeyboardMarkup(reply_keyboard_rating, one_time_keyboard=True)

reply_keyboard_menu = [['На главную']]
markup_menu = ReplyKeyboardMarkup(reply_keyboard_menu, one_time_keyboard=True)

reply_keyboard_film_recom = [['Любой', 'драма', 'мелодрама'], ['комедия', 'документальный', 'триллер'],
                             ['криминал', 'приключения', 'боевик']]
markup_film_recom = ReplyKeyboardMarkup(reply_keyboard_film_recom, one_time_keyboard=True)
# Диалоги
conv_handler = ConversationHandler(
    # Точка входа в диалог.
    # В данном случае — команда /start. Она задаёт первый вопрос.
    entry_points=[CommandHandler('start', start)],

    states={
        1: [MessageHandler(Filters.text, first_response, pass_user_data=True)],
        2: [MessageHandler(Filters.text, find_film, pass_user_data=True)],
        3: [MessageHandler(Filters.text, film_info, pass_user_data=True)],
        4: [MessageHandler(Filters.text, start, pass_user_data=True)],
        5: [MessageHandler(Filters.text, second_response, pass_user_data=True)],
        6: [MessageHandler(Filters.text, put_rating, pass_user_data=True)],
        7: [MessageHandler(Filters.text, choose_genre, pass_user_data=True)],
    },

    # Точка прерывания диалога. В данном случае — команда /stop.
    fallbacks=[CommandHandler('stop', stop)]
)

if __name__ == '__main__':
    pass
