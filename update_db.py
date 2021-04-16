from update_news import update_news
from update_questions import update_db_questions
import threading

if __name__ == '__main__':
    sprashivai = threading.Thread(target=update_db_questions())
    sprashivai.start()
    tofmal = threading.Thread(target=update_news)
    tofmal.start()
