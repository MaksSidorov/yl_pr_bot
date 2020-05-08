import sqlalchemy
from .db_session import SqlAlchemyBase


# Класс чтобы пользователи могли ставить оценки
class UserRating(SqlAlchemyBase):
    __tablename__ = 'user_rating'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    us_rating = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    film_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)


if __name__ == '__main__':
    print('user_rating')
