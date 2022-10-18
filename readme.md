Функцию, которая по заданному идентификатору поста возвращает ответ метода API.
Для хранения блокировок и рабочей информации используется REDIS.

Есть с API возвращающий информацию о посте https://api.com/posts/<id>
где <id> это идентификатор поста. API имеет ограничение по частоте запросов
до 30 раз в минуту. При превышении ограничения происходит временная
блокировка доступа. 

Необходимо иметь возможность обращаться к сервису в несколько раз чаще.
Для этого API уже сделаны зеркала,
api_addr = ['https://api.com/posts/', 'https://mirror1.com/posts/',]
Надо написать функцию на Python, которая по заданному идентификатору поста
будет возвращать ответ метода API. Для решения задачи можно использовать
любое бесплатное стороннее ПО и библиотеки.

Требования к функции:
1) Вызов функции не должен приводить к блокировке со стороны API.
2) Функция может вызываться одновременно из разных потоков и из
    разных процессов.
3) Функция должна эффективно использовать все доступные зеркала
    для доступа к API.
4) Любой разработчик команды должен иметь возможность вызывать
    функцию и просто получить результат.
  
