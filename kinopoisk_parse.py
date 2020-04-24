import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from data import db_session
from data import films


# Функция для парсинга списка фильмов
def parse_top_films(path='', numner_pages=0):
    for page in range(1, numner_pages + 1):
        page = requests.get(path.format(page), headers={'User-Agent': UserAgent().chrome})
        soup = BeautifulSoup(page.content, 'lxml')
        items = soup.find_all("div", {'class': 'name'})
        films_list = []
        for item in items:
            title = item.find('a').text
            film_id = item.find('a').get('href').split('/')[-2]
            films_list.append(get_film_info(title=title, film_id=film_id))

        return films_list


# Функция для получения информации о конкретном фильме
def parse_film_page(film_id=''):
    kino_path = 'https://www.kinopoisk.ru/film/{}/'.format(film_id)
    page = requests.get(kino_path, headers={'User-Agent': UserAgent().chrome})
    soup = BeautifulSoup(page.content, 'lxml')
    with open("test.html", "wb") as fh:
        fh.write(page.content)
    return soup


def get_film_info(title='', film_id=''):
    soup = parse_film_page(film_id=film_id)
    film_info = [film_id, title]
    film_info.append(float(soup.find("meta", {'itemprop': 'ratingValue'}).get('content')))
    items = soup.find("span", {'itemprop': 'genre'}).find_all('a')
    c = 0
    for i in items:
        film_info.append(i.text)
        c += 1
        if c > 3:
            break
    if c < 3:
        while c != 3:
            film_info.append('No_genre')
            c += 1

    return film_info


def add_in_db(data):
    db_session.global_init("db/kinobot_data.sqlite")
    for film_data in data:
        film = films.Film()
        film.film_id = int(film_data[0])
        film.title = film_data[1]
        film_data.rating = film_data[2]
        film.main_genre = film_data[3]
        film.genre_2 = film_data[4]
        film.genre_3 = film_data[5]
        session = db_session.create_session()
        session.add(film)
        session.commit()


def get_director():
    pass


if __name__ == '__main__':
    add_in_db(parse_top_films(
        path='https://www.kinopoisk.ru/top/navigator/m_act%5Brating%5D/6.4%3A/m_act%5Bis_film%5D/on/order/rating/page/{}/perpage/200/#results',
        numner_pages=56))
