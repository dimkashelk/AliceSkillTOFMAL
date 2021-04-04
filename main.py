import subprocess
import pymorphy2
from flask import Flask, request, send_file
import logging
from session import Session
import json
from random import randrange
from update_questions import update_db_questions
import threading

text_phrases = {
    'begin_phrase': ['Привет!', 'Здравствуйте, начнем?', 'Здравствуйте', 'Привет, начнем?'],
    'user_return': ['С возвращением!', 'Я вас так ждала'],
    'question': ['У Геннадия Рувимовича спрашивают:', 'Вот такой вопрос задали:', 'Вопрос:'],
    'answer': ['Геннадий Рувимович отвечает:', 'А вот так ответил Любич:', 'Ответ:'],
    'rules': ['Я могу рассказать вам последние вопросы Любичу на спрашивай, '
              'а так же прочитать новости с лицейского сайта',
              'Прочитать новости с лицейского сайта? Или вопросы с спрашивай? '
              'Да легко, просто спросите',
              'Спросите у меня, что происходит на спрашивай или на лицейском сайте. '
              'Так и задайте вопрос: "Что нового на тофмале?"'],
    'not_understand': ['Не понятно, попробуйте перефразировать',
                       'Что вы сказали?',
                       'Я вас не понимаю',
                       'Правила почитайте'],
    'about': ['Должность: \n Директор, учитель информатики\n\n'
              'Преподаваемые дисциплины: \n Информатика и ИКТ\n\n'
              'Специальность: \n Учитель информатики, инженер по автоматизации химических производств \n\n'
              'Квалификация: \nВысшая квалификационная категория\n\n'
              'Общий стаж работы: 29 лет\n\n'
              'Педагогический стаж: 25 лет\n\n'
              'Кабинет: 410']
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
    try:
        response = {
            'session': request.json['session'],
            'version': request.json['version'],
            'response': {
                'end_session': False,
            }
        }
    except BaseException:
        return 'Alice skill'
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = get_user_id(req)
    if req['session']['new'] and sessionStorage.get_user(user_id) is None:
        new_user(res=res, user_id=user_id)
        return
    res['response']['buttons'] = get_buttons('old_user')
    if req['session']['new']:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('user_return')
        return
    old_user(res=res, req=req, user_id=user_id)


def get_buttons(param):
    if param == 'new_user':
        dop = ['Что ты умеешь?']
    elif param == 'old_user':
        dop = ['Дальше', 'Что ты умеешь?']
    else:
        dop = []
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
    res['response']['buttons'] = get_buttons('new_user')
    sessionStorage.insert_new_user(user_id)


def get_random_phrases(type_phrases):
    return text_phrases[type_phrases][randrange(0, len(text_phrases[type_phrases]))]


def old_user(res, req, user_id):
    wants = what_user_want(req, user_id)
    if wants == 'sprashivai':
        number = -1
        for i in req['request']['nlu']['entities']:
            if i['type'] == 'YANDEX.NUMBER':
                number = i['value']
                break
        dop = sessionStorage.get_next_sprashivai(user_id, number)
        res['response']['text'] = \
            res['response']['tts'] = get_random_phrases(
            'question') + '\n' + dop[0] + '\n\n' + get_random_phrases(
            'answer') + '\n' + dop[1]
    elif wants == 'skill':
        res['response']['text'] = res['response']['tts'] = get_random_phrases('rules')
    elif wants == 'about':
        res['response']['text'] = res['response']['tts'] = get_random_phrases('about')
        res['response']['card'] = {}
        res['response']['card']['type'] = "BigImage"
        res['response']['card']['image_id'] = '1652229/a754a8a6586ac69c482b'
        res['response']['card']['title'] = 'Любич Геннадий Рувимович'
        res['response']['card']['description'] = get_random_phrases('about')
    else:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')


def what_user_want(req, user_id):
    tokens = req['request']['nlu']['tokens']
    morph = pymorphy2.MorphAnalyzer()
    for i, v in enumerate(tokens):
        tokens[i] = morph.parse(v)[0].normal_form
    if any(i in tokens for i in ['далёкий']):
        user = sessionStorage.get_user(user_id)
        return user.last
    if any(i in tokens for i in ['спрашивать', 'вопрос']):
        if any(i in tokens for i in ['новое', 'последний']):
            user = sessionStorage.get_user(user_id)
            user.number_question_sprashivai = 1
            sessionStorage.commit()
        return 'sprashivai'
    if any(i in tokens for i in ['уметь', 'мочь', 'правило']):
        return 'skill'
    if any(i in tokens for i in ['кто', 'он', 'такой', 'рассказать', 'любич']):
        return 'about'


if __name__ == '__main__':
    thread = threading.Thread(target=update_db_questions)
    thread.start()
    app.run()
