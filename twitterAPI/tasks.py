from celery import shared_task, Task
import twitterAPI.services.twitter_follower_service as services
from twitterAPI.exceptions import TooManyRequestsException


class BaseTaskWithRetry(Task):
    autoretry_for = (TooManyRequestsException,)
    max_retries = 20
    retry_backoff = 1800
    retry_backoff_max = 86400
    retry_jitter = True


@shared_task(base=BaseTaskWithRetry)
def fetch_follower_ids(user_id):
    services.TwitterFollowerService(user_id).fetch_follower_list()


@shared_task(base=BaseTaskWithRetry)
def fetch_follower_basic_info(user_id, follower_info):
    services.TwitterFollowerService(user_id).fetch_save_follower_activity_info(follower_info)


@shared_task(base=BaseTaskWithRetry)
def fetch_follower_last_like_date(user_id, follower_info):
    services.TwitterFollowerService(user_id).fetch_follower_last_like_date(follower_info)


@shared_task(base=BaseTaskWithRetry)
def fetch_follower_last_tweet_date(user_id, follower_info):
    services.TwitterFollowerService(user_id).fetch_follower_last_tweet_date(follower_info)


@shared_task(base=BaseTaskWithRetry)
def remove_follower(user_id, follower_id):
    services.TwitterFollowerService(user_id).remove_follower(follower_id)
