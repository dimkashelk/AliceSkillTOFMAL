import sqlalchemy
from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.INT, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, default='')
    answer = sqlalchemy.Column(sqlalchemy.String, default='')
    time = sqlalchemy.Column(sqlalchemy.String, default='', unique=True)
    url = sqlalchemy.Column(sqlalchemy.String, default='')
