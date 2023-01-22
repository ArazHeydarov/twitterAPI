from celery import shared_task, Task
import twitterAPI.services as services


class BaseTaskWithRetry(Task):
    autoretry_for = (FileNotFoundError,)
    max_retries = 5
    retry_backoff = 5
    retry_backoff_max = 700
    retry_jitter = False


@shared_task(base=BaseTaskWithRetry)
def fetch_follower_ids(user_id):
    services.TwitterFollowerService(user_id).fetch_follower_list()


@shared_task(base=BaseTaskWithRetry)
def fetch_follower_basic_info(user_id, follower_info):
    services.TwitterFollowerService(user_id).fetch_follower_basic_info(follower_info)


@shared_task(base=BaseTaskWithRetry)
def fetch_follower_last_like_date(user_id, follower_info):
    services.TwitterFollowerService(user_id).fetch_follower_last_like_date(follower_info)


@shared_task(base=BaseTaskWithRetry)
def fetch_follower_last_tweet_date(user_id, follower_info):
    services.TwitterFollowerService(user_id).fetch_follower_last_tweet_date(follower_info)
