'''Quite possibly the most simplistic remotely available todo list ever created'''
import os
from urllib.parse import urlparse

import hot_redis
import hug
import requests

__version__ = '0.0.1'
REDIS_AUTH = urlparse(os.environ.get('REDISCLOUD_URL'))
hot_redis.configure({'host': REDIS_AUTH.hostname, 'port': REDIS_AUTH.port or 6379, 'password': REDIS_AUTH.password})
todos = hot_redis.List(key='my_todos')
authentication = hug.authentication.basic(hug.authentication.verify('user1', 'password1'))


@hug.get('/todos')
def get_todos():
    '''Returns a list of all my todo items'''
    return list(todos)


@hug.post('/todos', requires=authentication)
def add_todo(todo):
    '''Adds a new todo item'''
    todos.append(todo)


@hug.delete('/todos', requires=authentication)
def remove_todo(todo):
    '''Removes a todo from the list'''
    todos.pop(todos.index(todo))


@hug.cli(version=__version__)
def todo(add=None, remove=None, endpoint='http://localhost:8000/todos', user='user1', password='password1'):
    '''A super simple remotely available todo list'''
    auth=(user, password)
    if add:
        return requests.post(endpoint, data={'todo': add}, auth=auth) and 'Successfully added todo'
    if remove:
        return requests.delete(endpoint, data={'todo': remove}, auth=auth) and 'Successfully removed/completed todo'

    return "\n".join(requests.get(endpoint, auth=auth).json())
