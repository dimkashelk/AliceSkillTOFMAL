from requests import post, get
from bs4 import BeautifulSoup
from time import sleep
from session import Session
from random import randint


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
    'Content-Length': '70',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'check=1; '
              'spr_c=ea9f7f019995713f0d1501fb7140ed97c74a7072f02b9afaea43a9e977360a7e; '
              'HWETZ=E77IPUIO; '
              '_ym_uid=161151562981861103; '
              '_ym_d=1611515629; '
              '_ga=GA1.2.992004252.1611515629; '
              '_gid=GA1.2.2121363628.1611515629; '
              '_ym_isad=2; '
              '_ym_visorc_805556=w; '
              '__gads=ID=421b5c5b02aba6c4-224c4c78a0b9002f:T=1611515555:S=ALNI_MZhkSDiOZ84CQthCOyS76L_N6ACtA; '
              '_fbp=fb.1.1611515629880.621869545',
    'DNT': '1',
    'Host': 'sprashivai.ru',
    'Origin': 'http://sprashivai.ru',
    'Referer': 'http://sprashivai.ru/lubichgr',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/87.0.4280.88 '
                  'YaBrowser/20.12.1.179 '
                  'Yowser/2.5 Safari/537.36',
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
        dop = post('http://sprashivai.ru/responses/load/new', headers=headers, data=data).json()
        bs = BeautifulSoup(dop['q_html'], 'lxml')
        for i in bs.find_all('div', attrs={'class': 'item'}):
            try:
                add_answers(i)
            except BaseException:
                pass
        session.add_questions(a)
        sleep(180)
