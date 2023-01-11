from celery import shared_task, Task
from time import sleep


@shared_task()
def test_func():
    return "Hello"
