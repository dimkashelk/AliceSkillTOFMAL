from requests import post, get
import requests
from bs4 import BeautifulSoup
from time import sleep
from session import Session
from random import randint
import cfscrape


def add_answers(i):
    global a, session, headers
    bs_dop = BeautifulSoup(f"<html> <body>{i}</body></html>", 'lxml')
    block = bs_dop.body.find('div', attrs={'class': 'item'})
    dop = []
    dop.append(block.find('div', attrs={'class': 'item_content'}).
               find('div', attrs={'class': 'inbox_question'}).text)
    dop.append(block.find('div', attrs={'class': 'item_content'}).
               find('div', attrs={'class': 'text_answer'}).text)
    dop.append(block.find('div', attrs={'class': 'item_content'}).
               find('div', attrs={'class': 'nq_time'}).
               find('a', attrs={'class': 'time_link'}).
               find('span', attrs={'class': 't_timer'}).
               find('span', attrs={'class': 't_st'}).text)
    a.append(dop)


headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '35',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': '_ym_uid=1596696468343546232; '
              '_ga=GA1.2.1694673686.1596696468; '
              'usersession=5063d8d29fcd51ac78a088ad86cd681bd3c2ff92d2f3bb491adcd77a56ed345c; '
              '__gads=ID=165efdf3256d4c85-22d1a12df9b80001:T=1602685204:RT=1602685204:S=ALNI_MaDxYq4AXYX9Q0Ux7dAHl9f6xjg0Q; '
              '_ym_d=1612538642; '
              '_fbp=fb.1.1614417207106.1185161453; '
              '_gid=GA1.2.1481418507.1616346835; '
              'HWETZ=E77IPUIO; '
              'cf_clearance=e3217de983e3f380f497792bc6ed62eeb0ab59db-1617525562-0-150; '
              '__cfduid=dbb127f86bce222149f4eb39b8fe0b86f1617525562; '
              'check=1; '
              'spr_c=4ca5a1ffe083926d9df7909623cd4b5a8952c6a1966da4ee59afe7f4eef3caa0; '
              '_ym_isad=1; '
              '_ym_visorc=w; '
              '__cf_bm=58d7b93c4b077516b1a48084d2368d76fc181e9a-1617530499-1800-ARA9OlqYe4Q1oNAhJ1CBRdRT6aJZRG/9iEEjQnd/cZS9EAFBZ3CGRKCN5OiWsdjY7tJPZeQgOegLNMHei4dRED1JOeprGpefBsz/R2XzyXoXEU6iRJU5jqk1Oj/WDbDjEA==; '
              '_gat_gtag_UA_70093472_2=1',
    'DNT': '1',
    'Host': 'sprashivai.ru',
    'Origin': 'http://sprashivai.ru',
    'Referer': 'http://sprashivai.ru/lubichgr',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 YaBrowser/21.2.4.165 Yowser/2.5 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
session = Session()
a = []


def update_db_questions():
    global a, session, headers
    while True:
        data = {
            'username': 'lubichgr',
            'offset': session.get_last_time()
        }
        try:
            dop = post('http://sprashivai.ru/responses/load/new', headers=headers, data=data).json()
        except BaseException:
            print("DON'T CONNECT TO sprashivai")
            sleep(randint(160, 250))
            continue
        bs = BeautifulSoup(dop['q_html'], 'lxml')
        for i in bs.find_all('div', attrs={'class': 'item'}):
            add_answers(i)
        try:
            session.add_questions(a)
        except BaseException:
            pass
        sleep(randint(160, 250))
