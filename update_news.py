import re
from requests import get
from session import Session
from time import sleep


def clean_html(raw_html):
    clean_r = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    clean_text = re.sub(clean_r, '', raw_html)
    clean_text = clean_text.replace('\r', ' ').replace('\t', ' ')
    return clean_text


def update_news():
    while True:
        res = get('http://tofmal.ru/api/news/?api-key=NoOfLj15L5ZVJxcyhASB_VUicIsdsfWh1t6viInlFUQ').json()
        a = {}
        for i in res['results']:
            a[i['id']] = {"title": i['title'],
                          "content": clean_html(i['content']).rstrip(),
                          "time": i['publication_time']}
        next = res['next']
        while True:
            try:
                res = get(next).json()
                for i in res['results']:
                    a[i['id']] = {"title": i['title'],
                                  "content": clean_html(i['content']).rstrip(),
                                  "time": i['publication_time']}
                next = res['next']
            except BaseException:
                break
        session = Session()
        session.add_newses(a)
        print("A")
        sleep(300)


update_news()
