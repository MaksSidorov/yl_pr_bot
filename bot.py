import urllib.request
ex = 'https://www.kinopoisk.ru/top/navigator/m_act[rating]/6.6%3A/order/rating/page/7/perpage/200/#results'

ex1 = 'https://www.kinopoisk.ru/top/navigator/m_act%5Brating%5D/6.4%3A/m_act%5Bis_film%5D/on/m_act%5Bis_mult%5D/on/order/rating/#results'

ex2 = 'https://www.kinopoisk.ru/top/navigator/m_act%5Brating%5D/6.4%3A/m_act%5Bis_film%5D/on/order/rating/page/1/perpage/200/#results'
import requests
from fake_useragent import UserAgent


# page_link = 'https://www.kinopoisk.ru/top/navigator/m_act[rating]/7.8%3A/order/rating/page/6/perpage/50/#results'
# page = requests.get('https://www.kinopoisk.ru/film/447301/', headers={'User-Agent': UserAgent().chrome})
#
#
# with open("test.html", "wb") as fh:
#     fh.write(page.content)
#
# exit(0)

from bs4 import BeautifulSoup

with open("test.html", "rb") as f:
    contents = f.read()

    soup = BeautifulSoup(contents, 'lxml')

    # print(soup.find("ul", attrs={ "id" : "mylist"}))
    items = soup.find("span", {'itemprop': 'genre'}).find_all('a')
    for i in items:
        print(i.text)
    print(items)