__author__ = 'eliashussen'
from celery import Celery

app = Celery('tasks', broker='redis://guest@localhost//')

@app.task
def add(x, y):
    return x + y

