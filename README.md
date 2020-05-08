# yl_pr_bot

## Код проекта находится в нескольких .py файлах
  + bot.py (скелет бота)
  + telegram_functions.py (Функции, клавиатуры и т. п, связанные с работой бота)
  + kinopoisk_parse.py (Функции, связанные с парсингом и получением данных с сайта kinopoisk.ru)
  
## Работа с базами данных
  + В проекте используется база данные kinobot_data.sqlite
  + В БД есть таблица films для храниение фильмов для рекомендации 
  + В БД есть таблица user_rating для хранения оценок пользователей

## Используемые библиотеки 
  + python-telegram-api - для создания бота
  + sqlalchemy - для работы с БД
  + requests - для запросов
  + BeautifulSoup4 - для парсинга сайтов
  + остальные бибилиотеки и зависимости находятся в файле requirements.txt
