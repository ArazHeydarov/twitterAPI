from celery import shared_task, Task
from time import sleep


@shared_task(autoretry_for=(ValueError,), retry_backoff=600, retry_jitter=False,
             max_retries=10, retry_backoff_max=False)
def test_func():
    return "Hello"
