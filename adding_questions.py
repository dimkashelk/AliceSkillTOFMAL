from requests import get
from bs4 import BeautifulSoup
from time import sleep
from pprint import pprint

res = get('http://sprashivai.ru/lubichgr').text
bs = BeautifulSoup(res, 'lxml')
blocks = bs.body.find('div', id='main_layout').find('div', id='content_layout').find('div',
                                                                                     id='user_responses').find_all(
    'div', attrs={'class': 'item'})
a = []
a.append(blocks[-1].find('div', attrs={'class': 'item_content'}).
         find('div', attrs={'class': 'inbox_question'}).text)
a.append(blocks[-1].find('div', attrs={'class': 'item_content'}).
         find('div', attrs={'class': 'text_answer'}).text)
a.append(blocks[-1].find('div', attrs={'class': 'nq_time'}).find('span', attrs={'class': 't_st'}).text)
print(a)
# http://sprashivai.ru/responses/load
b = {
    'POST': '/responses/load HTTP/1.1',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Length': '35',
    'Origin': 'http://sprashivai.ru',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'http://sprashivai.ru/lubichgr',
    'Cookie': 'check=1; spr_c=fab2b545b788e95e468f0eb7312eb0736254d63d49da89656487fa13abdb5717; HWETZ=E77IPUIO'
}
sleep(5)
res = get('http://sprashivai.ru/responses/load', headers=b, params={'username': 'lubichgr', 'offset': a[-1]})
pprint(res.json())
bs = BeautifulSoup(res, 'lxml')
blocks = bs.body.find('div', id='main_layout').find('div', id='content_layout').find('div',
                                                                                     id='user_responses').find_all(
    'div', attrs={'class': 'item'})
a = []
a.append(blocks[0].find('div', attrs={'class': 'item_content'}).
         find('div', attrs={'class': 'inbox_question'}).text)
a.append(blocks[0].find('div', attrs={'class': 'item_content'}).
         find('div', attrs={'class': 'text_answer'}).text)
a.append(blocks[0].find('div', attrs={'class': 'nq_time'}).find('span', attrs={'class': 't_st'}).text)
print(a)
