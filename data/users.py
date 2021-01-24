import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    number_news_tofmal = sqlalchemy.Column(sqlalchemy.INT, default=0)
    number_question_sprashivai = sqlalchemy.Column(sqlalchemy.INT, default=0)
    last = sqlalchemy.Column(sqlalchemy.String, default=0)
