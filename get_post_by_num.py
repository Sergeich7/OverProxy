"""Функция get_post_by_num() возвращает ответ API по заданному\
    идентификатору поста."""
#
# Есть с API возвращающий информацию о посте https://api.com/posts/<id>
# где <id> это идентификатор поста. API имеет ограничение по частоте запросов
# до 30 раз в минуту. При превышении ограничения происходит временная
# блокировка доступа. 
# Необходимо иметь возможность обращаться к сервису в несколько раз чаще.
# Для этого API уже сделаны зеркала,
# api_addr = ['https://api.com/posts/', 'https://mirror1.com/posts/',]
#
# Надо написать функцию на Python, которая по заданному идентификатору поста
# будет возвращать ответ метода API. Для решения задачи можно использовать
# любое бесплатное стороннее ПО и библиотеки.
#
# Требования к функции:
# 1) Вызов функции не должен приводить к блокировке со стороны API.
# 2) Функция может вызываться одновременно из разных потоков и из
#   разных процессов.
# 3) Функция должна эффективно использовать все доступные зеркала
#   для доступа к API.
# 4) Любой разработчик команды должен иметь возможность вызывать
#   функцию и просто получить результат.
#
#   18.10.2022
#

import requests
import random
import json
from datetime import timedelta

import redis

api_addr = [
    'https://api.com/posts/',
    'https://mirror1.com/posts/',
    ]

_LIFE_TIME_OF_FLAG = 61         # время жизни одного флага о запросе

_MAX_GET_1URL_PER_MIN = 29      # максимальное кол-во запросов через
                                # конкретный урл за 1 мин


def get_post_by_num(post_num=1, r_host='localhost', r_port=6379, r_pass=''):
    """Функция возвращает ответ API по заданному идентификатору поста."""
    # Возможно эта функция будет использоваться в ПО работающем на разных
    # компьютерах. Сохраняем промежуточную информацию в REDIS,
    # чтобы все имели к ней доступ отовсюду
    r = redis.StrictRedis(host=r_host, port=r_port, password=r_pass)

    p_urls = ''

    # Проверяем общую блокировку. На момент выбора прокси с базой
    # может работать только 1 процесс
    if r.get('total_blk'):
        return json.dumps({"error": "Total blockage."}, indent=2)

    r.setex('total_blk', timedelta(seconds=_LIFE_TIME_OF_FLAG), value=1)

    # собираем статистику из базы количество запросов
    # по каждому урлу за последнюю минуту
    # на каждый запрос создается ключ - живет _LIFE_TIME_OF_FLAG
    # url+https://mirror1.com/posts/+0.6290323885063988
    # ключ блокировки - живет до удаления или _LIFE_TIME_OF_FLAG
    # blk+https://mirror1.com/posts/+0.6290323885063988
    for addr in api_addr:
        if len(r.keys(f'blk+{addr}+*')) <= _MAX_GET_1URL_PER_MIN:
            p_urls = addr

    if not p_urls:
        r.delete('total_blk')
        return json.dumps({
            "error": "The maximum number of requests in the last 60 sec reached."
            }, indent=2)

    # нашли подходящий урл для запроса
    # сохраняем в redis ключи устаревающий через минуту
    sfx = random.random()
    # blk для запросов через этот урл пока не выполним запрос
    # сразу выставляем блокировку
    r.setex(
        f'blk+{p_urls}+{sfx}',
        timedelta(seconds=_LIFE_TIME_OF_FLAG), value='')
    # url для подсчета сколько было запросов через прокси
    r.setex(
        f'url+{p_urls}+{sfx}',
        timedelta(seconds=_LIFE_TIME_OF_FLAG), value='')

    # определились с прокси - снимаем общую блокировку
    r.delete('total_blk')

    # запрашиваем пост по номеру
    req = requests.get(f'{p_urls}{post_num}')

    # снимаем блокировку сразу после выполнения запроса
    r.delete(f'blk+{p_urls}+{sfx}')

    if req.status_code != 200:
        return json.dumps(
            {"error": f"Can not get post {post_num}. Status code: {req.status_code}"},
            indent=2)

    return req.text


if __name__ == "__main__":
    # самотестирование

    for i in range(70):
        print(get_post_by_num(i))
