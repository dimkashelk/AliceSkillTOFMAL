import subprocess
from ask_question import ask_question
import pymorphy2
from flask import Flask, request, send_file
import logging
from session import Session
import json
from random import randrange
from update_questions import update_db_questions
import threading
from update_news import update_news

text_phrases = {
    'begin_phrase': ['Привет! Ты можешь узнать, что нового на спрашивай у Любича. '
                     'Так и спроси: "Что нового на спрашивай"',
                     'Здравствуйте. Я могу прочитать новости с тофмала, '
                     'для этого спросите: "Что нового на сайте лицея?"',
                     'Здравствуйте. Задайте мне вопрос: "Что ты умеешь", а я расскажу, что могу',
                     'Привет. Спроси у меня, что я могу и я расскажу'],
    'user_return': ['С возвращением!',
                    'Я вас так ждала'],
    'question': ['У Геннадия Рувимовича спрашивают:',
                 'Вот такой вопрос задали:',
                 'Вопрос:'],
    'answer': ['Геннадий Рувимович отвечает:',
               'А вот так ответил Любич:',
               'Ответ:'],
    'rules': ['Я могу рассказать вам последние вопросы Любичу на спрашивай, '
              'а так же прочитать новости с лицейского сайта',
              'Прочитать новости с лицейского сайта? Или вопросы с спрашивай? '
              'Да легко, просто спросите',
              'Спросите у меня, что происходит на спрашивай или на лицейском сайте. '
              'Так и задайте вопрос: "Что нового на лицейском сайте?"'],
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
              'Кабинет: 410'],
    'not_found_question': ['Вопрос не найден',
                           'Такого вопроса нет в базе',
                           'Не удалось найти вопрос'],
    'not_found_news': ['Запись не найдена',
                       'Такой записи нет в базе',
                       'Не удалось найти запись',
                       'Новость не найдена',
                       'Такой новости нет в базе',
                       'Не удалось найти новость'],
    'news': ['Нашла такую запись:',
             'Давайте прочитаю:',
             'Это может быть интересно:'],
    'count_sprashivai': ['Сейчас я могу озвучить',
                         'Выбирайте один из',
                         'У меня'],
    'count_tofmal': ['Сейчас я могу озвучить',
                     'Выбирайте одну из',
                     'У меня',
                     'Сейчас на сайте'],
    'show_url': ['Я вас подожду',
                 'Смотрю, вам стало интересно',
                 'Возвращайтесь быстрее'],
    'ask_question': ['Озвучьте ваш вопрос и он будет отправлен:',
                     'Диктуйте вопрос:',
                     'Я слушаю, запоминаю и отправляю:',
                     'Вся во внимании:'],
    'send_question': ['Ваш вопрос отправлен',
                      'Все отправила. Теперь ждем ответа'],
    'not_send_question': ['Не удалось отправить вопрос, попробуйте позже',
                          'Извините, что-то сломалось. Ваш вопрос не отправлен'],
    'cancellation': ['Отменила',
                     'Хорошо, не будем спрашивать',
                     'Пусть это останется между нами',
                     'Вы можете продолжать, я не отправлю это']
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
        user = sessionStorage.get_user(user_id)
        user.listening_question = 0
        sessionStorage.commit()
        res['response']['text'] = res['response']['tts'] = get_random_phrases('user_return')
        return
    old_user(res=res, req=req, user_id=user_id)


def get_buttons(param, url=''):
    if param == 'new_user':
        dop = ['Что ты умеешь?']
    else:
        dop = ['Дальше', 'Что ты умеешь?']
    title = []
    for i in dop:
        title.append({
            "title": i.capitalize(),
            "hide": True
        })
    if url != '':
        if param == 'sprashivai':
            title.append({
                "title": "Посмотреть на sprashivai.ru",
                "hide": True,
                "url": url,
                "payload": {
                    "request": {
                        "command": "show",
                        "original_utterance": "show"
                    }
                }
            })
        elif param == 'tofmal':
            title.append({
                "title": "Посмотреть на tofmal.ru",
                "hide": True,
                "url": url,
                "payload": {
                    "request": {
                        "command": "show",
                        "original_utterance": "show"
                    }
                }
            })
        elif param == 'gr':
            title.append({
                "title": "Перейти на tofmal.ru",
                "hide": True,
                "url": url,
                "payload": {
                    "request": {
                        "command": "show",
                        "original_utterance": "show"
                    }
                }
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
        if dop is None:
            res['response']['text'] = \
                res['response']['tts'] = get_random_phrases('not_found_question')
            return
        res['response']['text'] = \
            res['response']['tts'] = fix_str(get_random_phrases(
                    'question') + '\n' + dop[0] + '\n\n' + get_random_phrases(
                    'answer') + '\n' + dop[1], mode='sprashivai')
        res['response']['buttons'] = get_buttons("sprashivai", f"http://sprashivai.ru{dop[2]}")
    elif wants == 'skill':
        res['response']['text'] = res['response']['tts'] = get_random_phrases('rules')
    elif wants == 'about':
        res['response']['text'] = res['response']['tts'] = get_random_phrases('about')
        res['response']['card'] = {}
        res['response']['card']['type'] = "BigImage"
        res['response']['card']['image_id'] = '1652229/a754a8a6586ac69c482b'
        res['response']['card']['title'] = 'Любич Геннадий Рувимович'
        res['response']['card']['description'] = get_random_phrases('about')
        res['response']['buttons'] = get_buttons("gr", f"https://tofmal.ru/people/employee/52")
    elif 'tofmal' in wants:
        number = -1
        for i in req['request']['nlu']['entities']:
            if i['type'] == 'YANDEX.NUMBER':
                number = i['value']
                break
        dop = None
        if wants == 'not_notice_tofmal':
            dop = sessionStorage.get_next_tofmal(user_id, number, is_notice=False)
        elif wants == 'notice_tofmal':
            dop = sessionStorage.get_next_tofmal(user_id, number, is_notice=True)
        if dop is None:
            res['response']['text'] = \
                res['response']['tts'] = get_random_phrases('not_found_news')
            return
        res['response']['text'] = \
            res['response']['tts'] = fix_str(get_random_phrases('news') + '\n' + dop[1] + '\n\n' + dop[2],
                                             mode='tofmal')
        res['response']['buttons'] = get_buttons("tofmal", f"https://tofmal.ru/news/{dop[0]}")
    elif wants == 'count_sprashivai':
        question_morph = pymorphy2.MorphAnalyzer().parse('вопрос')[0]
        count = sessionStorage.get_count_questions()
        res['response']['text'] = res['response']['tts'] = \
            get_random_phrases('count_sprashivai') + \
            f' {count} ' + \
            question_morph.make_agree_with_number(count).word
    elif wants == 'count_tofmal':
        news_morph = pymorphy2.MorphAnalyzer().parse('новость')[0]
        count = sessionStorage.get_count_news()
        res['response']['text'] = res['response']['tts'] = \
            get_random_phrases('count_news') + \
            f' {count} ' + \
            news_morph.make_agree_with_number(count).word
    elif wants == 'show':
        res['response']['text'] = res['response']['tts'] = get_random_phrases('show_url')
    elif wants == 'listening':
        res['response']['text'] = res['response']['tts'] = get_random_phrases('ask_question')
    elif wants == 'send_question':
        send = ask_question(req['request']['original_utterance'])
        if send:
            res['response']['text'] = res['response']['tts'] = get_random_phrases('send_question')
        else:
            res['response']['text'] = res['response']['tts'] = get_random_phrases('not_send_question')
    elif wants == 'cancellation':
        res['response']['text'] = res['response']['tts'] = get_random_phrases('cancellation')
    else:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')


def fix_str(string, mode='sprashivai'):
    if len(string) < 1024:
        return string
    else:
        if mode == 'sprashivai':
            return string[:990] + '\nСмотреть на sprashivai.ru'
        elif mode == 'tofmal':
            return string[:990] + '\nСмотреть на tofmal.ru'


def what_user_want(req, user_id):
    tokens = req['request']['nlu']['tokens']
    morph = pymorphy2.MorphAnalyzer()
    user = sessionStorage.get_user(user_id)
    if user.listening_question:
        if any(i in tokens for i in ['отмена', 'перестать']):
            user.listening_question = 0
            sessionStorage.commit()
            return 'cancellation'
        user.listening_question = 0
        sessionStorage.commit()
        return 'send_question'
    for i, v in enumerate(tokens):
        tokens[i] = morph.parse(v)[0].normal_form
    if any(i in tokens for i in ['спросить', 'узнать', 'задать', 'отправить']):
        user.listening_question = 1
        return 'listening'
    if any(i in tokens for i in ['далёкий', 'следующий', 'последующий']):
        return user.last
    if any(i in tokens for i in ['спрашивать', 'вопрос']):
        if any(i in tokens for i in ['новое', 'последний', 'новый', 'актуальный',
                                     'обновление', 'сначала', 'снова', 'начало']):
            user.number_question_sprashivai = 1
            sessionStorage.commit()
        elif any(i in tokens for i in ['количество', 'сколько', 'весь']):
            return 'count_sprashivai'
        return 'sprashivai'
    if any(i in tokens for i in ['уметь', 'мочь', 'правило', 'помочь', 'помощь']):
        return 'skill'
    if any(i in tokens for i in ['кто', 'он', 'такой', 'любич']):
        return 'about'
    if any(i in tokens for i in ['сайт', 'лицей', 'новость', 'анонс']):
        if any(i in tokens for i in ['анонс']):
            if any(i in tokens for i in ['новое', 'последний', 'новый', 'актуальный',
                                         'обновление', 'сначала', 'снова', 'начало']):
                user.number_news_tofmal_notice = 1
                user.last = 'notice_tofmal'
                sessionStorage.commit()
            return 'notice_tofmal'
        elif any(i in tokens for i in ['новое', 'последний', 'новый', 'актуальный',
                                       'обновление', 'сначала', 'снова', 'начало']):
            user.number_news_tofmal_not_notice = 1
        elif any(i in tokens for i in ['количество', 'сколько', 'весь']):
            return 'count_tofmal'
        user.last = 'not_notice_tofmal'
        sessionStorage.commit()
        return 'not_notice_tofmal'
    if req['request']['type'] == 'ButtonPressed' and 'посмотреть' in req['request']['nlu']['tokens']:
        return 'show'
    return 'not_understand'


if __name__ == '__main__':
    # sprashivai = threading.Thread(target=update_db_questions)
    # sprashivai.start()
    # tofmal = threading.Thread(target=update_news)
    # tofmal.start()
    app.run()
