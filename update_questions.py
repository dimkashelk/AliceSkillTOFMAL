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
    dop.append(block.find('div', attrs={'class': 'item_content'}).
               find('div', attrs={'class': 'nq_time'}).
               find('a', attrs={'class': 'time_link'}).get('href'))
    a.append(dop)


headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '35',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': '__cfduid=db6a69658ea1d926c8e80498af38c01981618507402; '
              'check=1; '
              'spr_c=4ca5a1ffe083926d9df7909623cd4b5a8952c6a1966da4ee59afe7f4eef3caa0; '
              'HWETZ=E77IPUIO; '
              '__cf_bm=6a4061b8a16f060ef42da1cf3c992da6b8198670-1618507426-1800-AdsPtk7ZR/skmpWBdNVGvY5WfV4zDO8DfZkbUQe2qxY6LTssrqL9sRvldUbwRByKWsWXZxM9C8kclU1q6K5Da7ysR7pqfQsaO21iZbgoyE8HQ2pmjAc33kxR1mxzP5m+DQ==; '
              '_ym_uid=1618507438169224150; '
              '_ym_d=1618507438; '
              '_ym_visorc=w; '
              '_ym_isad=1; '
              '__gads=ID=85faea34454aafb2-2252af8b17bb00d5:T=1618507442:RT=1618507442:S=ALNI_MZbomvRpp8MyA3lvZ9-izIQJPemtg; '
              '_fbp=fb.1.1618507452167.1870448315; '
              '_ga=GA1.2.1226048678.1618507438; '
              '_gid=GA1.2.1255317375.1618507458; '
              '_gat_gtag_UA_70093472_2=1',
    'DNT': '1',
    'Host': 'sprashivai.ru',
    'Origin': 'http://sprashivai.ru',
    'Referer': 'http://sprashivai.ru/lubichgr',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.86 '
                  'YaBrowser/21.3.1.91 '
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
        try:
            dop = post('http://sprashivai.ru/responses/load/new', headers=headers, data=data)
            print(dop, file=open('dop.txt', 'w'))
            print(dop, file=open('content.txt', 'w'))
            dop = dop.json()
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
