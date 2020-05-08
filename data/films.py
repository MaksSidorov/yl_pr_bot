import sqlalchemy
from .db_session import SqlAlchemyBase


# Данные о фильме чтобы порекомендовать его
class Film(SqlAlchemyBase):
    __tablename__ = 'films'

    film_id = sqlalchemy.Column(sqlalchemy.Integer,
                                primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    rating = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    main_genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    genre_2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    genre_3 = sqlalchemy.Column(sqlalchemy.String, nullable=True)


if __name__ == '__main__':
    print('films')
