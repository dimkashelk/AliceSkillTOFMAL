import sqlalchemy
from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase):
    __tablename__ = 'news_notice'

    id = sqlalchemy.Column(sqlalchemy.INT, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String)
    time = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String)
    tofmal_id = sqlalchemy.Column(sqlalchemy.INT)
    is_notice = sqlalchemy.Column(sqlalchemy.Boolean)
