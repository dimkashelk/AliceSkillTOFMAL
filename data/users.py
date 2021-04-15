import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    number_news_tofmal_not_notice = sqlalchemy.Column(sqlalchemy.INT, default=1)
    number_news_tofmal_notice = sqlalchemy.Column(sqlalchemy.INT, default=1)
    number_question_sprashivai = sqlalchemy.Column(sqlalchemy.INT, default=1)
    last = sqlalchemy.Column(sqlalchemy.String, default='sprashivai')
    listening_question = sqlalchemy.Column(sqlalchemy.INT, default=0)
