import subprocess
import pymorphy2
from requests import get
from bs4 import BeautifulSoup
from flask import Flask, request, send_file
import logging
from session import Session
import json
from random import randrange

text_phrases = {
    'begin_phrase': ['Привет!', 'Здравствуйте, начнем?', 'Здравствуйте', 'Привет, начнем?'],
    'user_return': ['С возвращением!', 'Я вас долго ждала'],
    'question': ['У Геннадия Рувимовича спрашивают:', 'Вот такой вопрос задали:', 'Вопрос:'],
    'answer': ['Геннадий Рувимович отвечает:', 'А вот так ответил Любич:', 'Ответ:'],
    'rules': ['Я могу рассказать вам последние вопросы Любичу на спрашивай, '
              'а так же прочитать новости с лицеского сайта',
              'Прочитать новости с лицейского сайта? Или вопросы с спрашивай? '
              'Да легко, просто спросите',
              'Спросите у меня, что происходит на спрашивай или на лицейском сайте. '
              'Так и задайте вопрос: "Что нового на тофмале?"']
}

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log')

sessionStorage = Session()


@app.route('/log')
def get_log():
    return send_file('app.log')


@app.route('/update')
def update():
    process = subprocess.Popen('/bin/bash update_from_git.sh'.split())
    return 'request accepted'


@app.route('/', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False,
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = get_user_id(req)
    if req['session']['new'] and sessionStorage.get_user(user_id) is None:
        new_user(res=res, user_id=user_id)
        return
    res['response']['buttons'] = get_buttons()
    if req['session']['new']:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('user_return')
        return
    old_user(res=res, req=req, user_id=user_id)


def get_buttons():
    dop = ['Дальше', 'Что ты умеешь?']
    title = []
    for i in dop:
        title.append({
            "title": i.capitalize(),
            "hide": True
        })
    return title


def get_user_id(req):
    if req['session'].get('user', False):
        return req['session']['user']['user_id']
    return req['session']['application']['application_id']


def new_user(res, user_id):
    res['response']['text'] = res['response']['tts'] = get_random_phrases('begin_phrase')
    sessionStorage.insert_new_user(user_id)


def get_random_phrases(type_phrases):
    return text_phrases[type_phrases][randrange(0, len(text_phrases[type_phrases]))]


def old_user(res, req, user_id):
    wants = what_user_want(req, user_id)
    if wants == 'sprashivai':
        user = sessionStorage.get_user(user_id)
        for i in req['request']['nlu']['entities']:
            if i['type'] == 'YANDEX.NUMBER':
                user.number_question_sprashivai = i['value']
                break
        user = sessionStorage.get_user(user_id)
        number = user.number_question_sprashivai
        user.last = 'sprashivai'
        if number == 0:
            user.number_question_sprashivai += 1
            number = user.number_question_sprashivai
        if 1 <= number <= 10:
            dop = sprashai(number)
            res['response']['text'] = res['response']['tts'] = get_random_phrases('question') + '\n' + dop[0] + \
                                                               '\n\n' + get_random_phrases('answer') + '\n' + dop[1]
            if number == 10:
                user.number_question_sprashivai = 1
            else:
                user.number_question_sprashivai += 1
        else:
            res['response']['text'] = res['response']['tts'] = 'Пока так далеко я не умею смотреть'
        sessionStorage.commit()
    elif wants == 'skill':
        res['response']['text'] = res['response']['tts'] = get_random_phrases('rules')
    else:
        res['response']['text'] = res['response']['tts'] = 'Функционал расширяется со временем, ждите новых функций. ' \
                                                           'Очередь: бесконечное количество вопросов ' \
                                                           '(пока только первые 10), ' \
                                                           'комментарии, ' \
                                                           'прикрепленные картинки, ' \
                                                           'новости на tofmal'


def sprashai(number):
    res = get('http://sprashivai.ru/lubichgr').text
    bs = BeautifulSoup(res, 'lxml')
    blocks = bs.body.find('div', id='main_layout').find('div', id='content_layout').find('div',
                                                                                         id='user_responses').find_all(
        'div', attrs={'class': 'item'})
    a = []
    a.append(blocks[number - 1].find('div', attrs={'class': 'item_content'}).
             find('div', attrs={'class': 'inbox_question'}).text)
    a.append(blocks[number - 1].find('div', attrs={'class': 'item_content'}).
             find('div', attrs={'class': 'text_answer'}).text)
    return a


def what_user_want(req, user_id):
    tokens = req['request']['nlu']['tokens']
    morph = pymorphy2.MorphAnalyzer()
    for i, v in enumerate(tokens):
        tokens[i] = morph.parse(v)[0].normal_form
    if any(i in tokens for i in ['далёкий']):
        user = sessionStorage.get_user(user_id)
        return user.last
    if any(i in tokens for i in ['спрашивать', 'вопрос', 'любич']):
        if any(i in tokens for i in ['новое', 'последний']):
            user = sessionStorage.get_user(user_id)
            user.number_question_sprashivai = 1
            sessionStorage.commit()
        return 'sprashivai'
    if any(i in tokens for i in ['уметь', 'мочь', 'правило']):
        return 'skill'


if __name__ == '__main__':
    app.run()
