import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from data import db_session
from data import films
import time

not_in_films = []
not_in_pages = []

import socks
import socket

socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
socket.socket = socks.socksocket

headers = {
    'User-Agent': UserAgent().chrome
}


# Функция для парсинга списка фильмов
def parse_top_films(path='', numner_pages=0):
    films_list = []
    for page_num in range(1, numner_pages + 1):
        page = requests.get(path.format(page_num), headers=headers)
        print(path.format(page_num))
        soup = BeautifulSoup(page.content, 'lxml')
        items = soup.find_all("div", {'class': 'name'})
        films_page = []
        flag = True
        with open("lst.html", "wb") as fh:
            fh.write(page.content)
        for item in items:
            title = item.find('a').text
            film_id = item.find('a').get('href').split('/')[-2]
            print(film_id)
            flag = False
            films_page.append(get_film_info(title=title, film_id=film_id))
            add_in_db([films_page[-1]])
            time.sleep(10)

        time.sleep(10)
        if flag:
            not_in_pages.append(str(page_num))

        films_list.extend(films_page)

    return films_list


# Функция для получения информации о конкретном фильме
def parse_film_page(film_id=''):
    kino_path = 'https://www.kinopoisk.ru/film/{}/'.format(film_id)
    page = requests.get(kino_path, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    print(kino_path)
    with open("page.html", "wb") as fh:
        fh.write(page.content)
    return soup


def get_film_info(title='', film_id=''):
    soup = parse_film_page(film_id=film_id)
    film_info = [film_id, title]
    try:
        film_info.append(float(soup.find("meta", {'itemprop': 'ratingValue'}).get('content')))
        items = soup.find("span", {'itemprop': 'genre'}).find_all('a')
        c = 0
        for i in items:
            film_info.append(i.text)
            c += 1
            if c >= 3:
                break
        if c < 3:
            while c != 3:
                film_info.append('No_genre')
                c += 1
    except:
        print('НЕ удалось', title)
        film_info = []
        not_in_films.append(str(film_id))

    print(film_info)
    return film_info


def add_in_db(data):
    if data == [[]]:
        return 1
    db_session.global_init("db/kinobot_data.sqlite")
    for film_data in data:
        print(film_data)
        film = films.Film()
        film.film_id = int(film_data[0])
        film.title = film_data[1]
        film.rating = float(film_data[2])
        film.main_genre = film_data[3]
        film.genre_2 = film_data[4]
        film.genre_3 = film_data[5]
        session = db_session.create_session()
        session.add(film)
        session.commit()


def get_director(film_id='447301'):
    soup = parse_film_page(film_id=film_id)
    return soup.find("td", {'itemprop': 'director'}).find('a').text


def get_poster(film_id='447301'):
    soup = parse_film_page(film_id=film_id)
    return soup.find("img", {'itemprop': 'image'}).get('src')


def get_description(film_id='447301'):
    soup = parse_film_page(film_id=film_id)
    return soup.find("div", {'itemprop': 'description'}).text


def get_all_info(film_id='447301'):
    soup = parse_film_page(film_id=film_id)
    info = []
    descr = ['{} - {} ', 'Режиссер - {}', '{}']
    info.append(soup.find("span", {'class': 'moviename-title-wrapper'}).text)
    info.append(float(soup.find("meta", {'itemprop': 'ratingValue'}).get('content')))
    info.append(soup.find("td", {'itemprop': 'director'}).find('a').text)
    info.append(soup.find("div", {'itemprop': 'description'}).text)
    return ['\n'.join(descr).format(*info), soup.find("img", {'itemprop': 'image'}).get('src')]


if __name__ == '__main__':
    parse_top_films(
        path='https://www.kinopoisk.ru/top/navigator/m_act%5Brating%5D/6.4%3A/m_act%5Bis_film%5D/on/order/rating/page/{}/perpage/200/#results',
        numner_pages=20)

    with open('not_films.txt', 'w') as nf:
        nf.write('\n'.join(not_in_films))

    with open('not_page.txt', 'w') as np:
        np.write('\n'.join(not_in_pages))
    # print(get_description().replace('<br>', '\n'))
