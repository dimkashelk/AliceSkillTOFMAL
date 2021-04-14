from data import users, db_session, questions, news
from datetime import datetime


class Session:

    def __init__(self):
        db_session.global_init('db/db.db')
        self.session = db_session.create_session()

    def insert_new_user(self, user_id):
        user = users.User(id=user_id)
        self.session.add(user)
        self.session.commit()

    def get_user(self, user_id):
        user = self.session.query(users.User).filter(users.User.id == user_id).first()
        return user

    def commit(self):
        self.session.commit()

    def add_question(self, question_text, answer, time):
        question = questions.Question()
        question.question = question_text
        question.answer = answer
        question.time = time
        self.session.add(question)
        self.session.commit()

    def get_question(self, id):
        return self.session.query(questions.Question).filter(questions.Question.id == id).first()

    def reverse(self):
        all_questions = []
        i = 1
        question = self.get_question(i)
        while question is not None:
            all_questions.append([question.question, question.answer, question.time])
            i += 1
            question = self.get_question(i)
        self.session.execute("DELETE FROM questions")
        for i, v in enumerate(all_questions[::-1]):
            self.add_question(v[0], v[1], v[2])

    def add_questions(self, list_questions, reverse=True):
        len_questions = 0
        if reverse:
            for i in list_questions[::-1]:
                if self.get_question_by_time(i[2]) is None:
                    self.add_question(i[0], i[1], i[2])
                    len_questions += 1
        else:
            for i in list_questions:
                try:
                    self.add_question(i[0], i[1], i[2])
                    len_questions += 1
                except BaseException:
                    pass
        list_users = self.session.query(users.User).all()
        for user in list_users:
            user.number_question_sprashivai += len_questions
        self.session.commit()

    def get_count_questions(self):
        return len(self.session.query(questions.Question).all())

    def get_question_by_time(self, time):
        return self.session.query(
            questions.Question).filter(questions.Question.time == time).first()

    def get_last_time(self):
        count_question = self.get_count_questions()
        question = self.get_question(count_question)
        return question.time

    def get_next_sprashivai(self, user_id, number=-1):
        user = self.session.query(users.User).filter(users.User.id == user_id).first()
        user.last = 'sprashivai'
        if number == -1:
            question = self.session.query(
                questions.Question).filter(
                questions.Question.id ==
                self.get_count_questions() - user.number_question_sprashivai + 1).first()
        else:
            question = self.session.query(
                questions.Question).filter(
                questions.Question.id ==
                self.get_count_questions() - number + 1).first()
            user.number_question_sprashivai = number
        user.number_question_sprashivai += 1
        self.session.commit()
        return question.question, question.answer

    def add_news(self, content, time, title, tofmal_id):
        new = news.News()
        new.title = title
        new.content = content
        new.time = time
        new.tofmal_id = tofmal_id
        self.session.add(new)
        self.session.commit()

    def get_count_news(self):
        return len(self.session.query(news.News).all())

    def add_newses(self, dict_news):
        count = 0
        for i in sorted(dict_news.keys(),
                        key=lambda x: datetime.fromisoformat(dict_news[x]['time'])
                        )[self.get_count_news():]:
            self.add_news(dict_news[i]['content'], dict_news[i]['time'], dict_news[i]['title'], i)
            count += 1
        list_users = self.session.query(users.User).all()
        for user in list_users:
            user.number_news_tofmal += count
        self.session.commit()

    def get_next_tofmal(self, user_id, number=-1):
        user = self.session.query(users.User).filter(users.User.id == user_id).first()
        user.last = 'tofmal'
        if number == -1:
            new = self.session.query(
                news.News).filter(
                news.News.id ==
                self.get_count_news() - user.number_news_tofmal + 1).first()
        else:
            new = self.session.query(
                news.News).filter(
                news.News.id ==
                self.get_count_news() - number + 1).first()
            user.number_news_tofmal = number
        user.number_news_tofmal += 1
        self.session.commit()
        return new.id, new.title, new.content
