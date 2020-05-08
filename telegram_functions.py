from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import requests
from kinopoisk_parse import *
from data import db_session, user_rating

# Жанры
GENRES = ['детский', 'военный', 'музыка', 'фильм-нуар', 'ужасы', 'боевик', 'спорт', 'концерт', 'фэнтези', 'детектив',
          'фантастика', 'мюзикл', 'комедия', 'драма', 'документальный', 'семейный', 'криминал', 'биография', 'вестерн',
          'триллер', 'мелодрама', 'приключения', 'церемония', 'история', 'любой']


# ФУНКЦИИ
# Стартовая функция
def start(update, context):
    update.message.reply_text(
        "Привет! Я кино-бот. Я помогу тебе выбрать фильм, что вы хотите?", reply_markup=markup_start)

    return 1


# Остановочная функция
def stop(update, context):
    update.message.reply_text(
        "Пока", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


# Выбор направления
def first_response(update, context):
    resp = update.message.text
    if resp == 'Найти фильм':
        update.message.reply_text('Как называется фильм, который вам интересен?', reply_markup=ReplyKeyboardRemove())
        return 2
    elif resp == 'Порекомендовать фильм':
        update.message.reply_text('Выберите жанр', reply_markup=markup_film_recom)
        return 7
    elif resp == 'Найти ближ. кинотеатр':
        update.message.reply_text('С какой версии приложения вы сидите', reply_markup=markup_loc)
        return 9
    else:
        update.message.reply_text('Используйте кнопки')


# Поиск фильмов
def find_film(update, context):
    title = update.message.text
    # Поиск фильма по названию на КП
    res = kp_film_find(title.lower())
    # Если функция возвращает 3 фильма их выводят, иначе вывод сообщение об ошибке
    if len(res[0]) == 3:
        context.user_data['res'] = res
        update.message.reply_text(
            "Какой из этих фильмов ваш? \n" + "\n".join(res[0]), reply_markup=markup_choose)

        return 3
    else:
        update.message.reply_text("По данному запросу нет вариантов, попробуйте найти фильм сами",
                                  reply_markup=markup_film2)

        return 8


# Информация о фильме
def film_info(update, context):
    film_ch = update.message.text
    # Выбор фильма
    if film_ch in ['1', '2', '3']:
        context.user_data['film_id'] = context.user_data['res'][1][int(film_ch) - 1]
        context.user_data['film_title'] = context.user_data['res'][0][int(film_ch) - 1]
        # Информация о фильме [<крастое описание фильма>, <url а постер>]
        inf = get_all_info(film_id=context.user_data['film_id'])
        update.message.reply_text(inf[0], reply_markup=markup_film1)
        context.bot.sendPhoto(chat_id=update.message.chat_id, photo=inf[1])

        return 5
    elif film_ch == 'Нету':
        update.message.reply_text('Тогда попробуйте найти сами', reply_markup=markup_film2)

        return 8
    else:
        update.message.reply_text('Используйте кнопки')


# Выбор варианта
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
    else:
        update.message.reply_text('Используйте кнопки')


# Добавлние оценок фильмам
def put_rating(update, context):
    rating = update.message.text
    # Если оценка с неправильные типом или не в промежутке от 0 до 10, она становится 0
    try:
        float_rating = float(rating)
    except TypeError as E:
        float_rating = 0.0
    if float_rating > 10 or float_rating < 0:
        float_rating = 0.0
    # Добавление оценки
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


# Рекомендация фильма
def choose_genre(update, context):
    genre = update.message.text.lower()
    # Проверка жанра на наличие
    if genre.lower() in GENRES:
        # Подбор фильма в БД
        db_session.global_init("db/kinobot_data.sqlite")
        session = db_session.create_session()
        if genre == 'любой':
            films_list = session.query(films.Film).order_by(films.Film.rating.desc()).all()
        else:
            films_list = session.query(films.Film).filter(
                films.Film.main_genre == genre).order_by(
                films.Film.rating.desc()).all()
        c = 0
        filmss = []
        # Выбираем первые три фильма отсортированных по рейтингу, которые пользователь не оценил
        for film in films_list:
            f = session.query(user_rating.UserRating). \
                filter(user_rating.UserRating.film_id == film.film_id,
                       user_rating.UserRating.user_id == update.message.from_user.id).all()

            if len(f) == 0:
                c += 1
                filmss.append(film)
            if c >= 3:
                break
        update.message.reply_text(
            "Какой фильм выберите \n1. {} - {} \n2. {} - {} \n3. {} - {}".format(filmss[0].title, filmss[0].rating,
                                                                                 filmss[1].title,
                                                                                 filmss[0].rating, filmss[1].title,
                                                                                 filmss[2].rating),
            reply_markup=markup_choose)
        context.user_data['res'] = [[filmss[0].title, filmss[1].title, filmss[2].title],
                                    [filmss[0].film_id, filmss[1].film_id, filmss[2].film_id]]

        return 3
    else:
        update.message.reply_text(
            'Такого жанр нет. Возможно вы ошиблись, попробуйте написать корректно или используйте кнопки.')


def third_response(update, context):
    resp = update.message.text
    if resp == 'Искать снова':
        update.message.reply_text('Как называется фильм, который вам интересен?', reply_markup=ReplyKeyboardRemove())
        return 2
    elif resp == 'В главное меню':
        update.message.reply_text('На главную',
                                  reply_markup=markup_menu)
        return 4
    else:
        update.message.reply_text('Используйте кнопки')


# Выбор устройста с которого сидит человек
def location_kino(update, context):
    resp = update.message.text
    if resp == 'С мобильной версии':
        update.message.reply_text('Хорошо, тогда поделитесь геолокацией', reply_markup=markup_loc_phone)

        return 10
    elif resp == 'С Telegram Desktop':
        update.message.reply_text('Хорошо, тогда передайте свое местоположение в формате \n<Город> <улица> <дом>',
                                  reply_markup=ReplyKeyboardRemove())

        return 11
    elif resp == 'В главное меню':
        update.message.reply_text('На главную',
                                  reply_markup=markup_menu)
        return 4
    else:
        update.message.reply_text('Используйте кнопки')


# Поиск кинотеатра с телефона
def location_kino_phone(update, context):
    resp = update.message.location
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    # Передаем координаты пользователя
    address_ll = "{},{}".format(resp['longitude'], resp['latitude'])

    search_params = {
        "apikey": api_key,
        "text": "кинотеатр",
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()
    organization = json_response["features"][0]
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    update.message.reply_text('Кинотеатр ' + org_name + ' ' + org_address,
                              reply_markup=markup_menu)
    return 4


# Поиск кинотеатра с Telegram Desktop
def location_kino_desktop(update, context):
    resp = update.message.text
    toponym_to_find = " ".join(resp.split())

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    address_ll = "{},{}".format(toponym_longitude, toponym_lattitude)

    search_params = {
        "apikey": api_key,
        "text": "кинотеатр",
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()
    organization = json_response["features"][0]
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    update.message.reply_text('Кинотеатр' + org_name + ' ' + org_address,
                              reply_markup=markup_menu)
    return 4


# Клавиатуры
reply_keyboard_start = [['Найти фильм', 'Порекомендовать фильм'], ['Найти ближ. кинотеатр']]
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

reply_keyboard_film2 = [['Искать снова', 'В главное меню']]
markup_film2 = ReplyKeyboardMarkup(reply_keyboard_film2, one_time_keyboard=True)

reply_keyboard_loc = [['С мобильной версии', 'С Telegram Desktop'], ['В главное меню']]
markup_loc = ReplyKeyboardMarkup(reply_keyboard_loc, one_time_keyboard=True)

reply_keyboard_loc_phone = [[KeyboardButton(text='Дать геолокацию', request_location=True), 'В главное меню']]
markup_loc_phone = ReplyKeyboardMarkup(reply_keyboard_loc_phone, one_time_keyboard=True)
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
        8: [MessageHandler(Filters.text, third_response, pass_user_data=True)],
        9: [MessageHandler(Filters.text, location_kino, pass_user_data=True)],
        10: [MessageHandler(Filters.location, location_kino_phone, pass_user_data=True)],
        11: [MessageHandler(Filters.text, location_kino_desktop, pass_user_data=True)],
    },

    # Точка прерывания диалога. В данном случае — команда /stop.
    fallbacks=[CommandHandler('stop', stop)]
)

if __name__ == '__main__':
    pass
