import math
import logging
from twitterAPI.repos.twitter_user_repo import TwitterUserRepo
from twitterAPI.repos.twitter_follower_repo import TwitterFollowersRepo
from twitterAPI.clients.twitter_client import TwitterClient
import twitterAPI.tasks as tasks
from twitterAPI.utils import process_profile_picture, get_follower_ids_to_remove
from twitterAPI.settings import OBJECTS_PER_PAGE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s - %(levelname)s] [%(module)s:%(funcName)s] | %(message)s')
handler = logging.FileHandler('./logs/services.log', mode='a', encoding='utf-8')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


class TwitterFollowerService:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.twitter_user = TwitterUserRepo.fetch_twitter_user_by_id(self.user_id)
        self.twitter_client = TwitterClient(self.twitter_user)
        self.twitter_followers_repo = TwitterFollowersRepo(self.twitter_user)

    def get_followers(self, request_params: dict):
        logger.info(f'Fetching followers for user {self.user_id}')
        filters = self._formulate_filters(request_params)
        order = self._formulate_order(request_params)
        offset = (int(request_params.get('page', 1)) - 1) * OBJECTS_PER_PAGE
        all_followers_count = self.twitter_followers_repo.fetch_followers_count(currently_following=True)
        followers, follower_count = self.twitter_followers_repo.fetch_followers(currently_following=True,
                                                                                filters=filters,
                                                                                order=order, offset=offset)
        page_numbers = [index for index in range(2, math.ceil(follower_count / OBJECTS_PER_PAGE) + 1)]
        logger.info(f'Fetched {follower_count} followers for user {self.user_id}')
        return followers, page_numbers, all_followers_count

    @staticmethod
    def _formulate_filters(request_params: dict):
        filters = {}
        if request_params.get('last_like_dt'):
            filters['last_like_dt__lte'] = request_params.get('last_like_dt')
        if request_params.get('last_tweet_dt'):
            filters['last_tweet_dt__lte'] = request_params.get('last_tweet_dt')
        return filters

    @staticmethod
    def _formulate_order(request_params: dict):
        order = []
        if request_params.get('last_like_dt_sort_asc') == 'true':
            order.append('last_like_dt')
        else:
            order.append('-last_like_dt')
        if request_params.get('last_tweet_dt_sort_asc') == 'true':
            order.append('last_tweet_dt')
        else:
            order.append('-last_tweet_dt')
        return order

    def update_followers(self):
        logger.info(f'Updating followers for user {self.user_id}')
        self.twitter_followers_repo.update_followers_following_status()
        tasks.fetch_follower_ids.delay(self.user_id)

    def fetch_follower_list(self):
        logger.info(f'Fetching follower list for user {self.user_id}')
        follower_list = self.twitter_client.fetch_followers_list()
        for follower in follower_list:
            tasks.fetch_follower_basic_info.delay(self.user_id, follower)

    def fetch_save_follower_activity_info(self, follower_info: dict):
        logger.info(f'Fetching follower named {follower_info["name"].encode("utf-8")} '
                    f'basic info for user {self.user_id}')
        follower_with_info = {'twitter_user_id': follower_info['id'],
                              'name': follower_info.get('name'),
                              'username': follower_info.get('username'),
                              'pp_url': process_profile_picture(follower_info.get('profile_image_url')),
                              'protected': follower_info.get('protected'),
                              'verified': follower_info.get('verified'),
                              'location': follower_info.get('location'),
                              'description': follower_info.get('description'),
                              'currently_following': True,
                              'profile_created_at': follower_info.get('created_at')}
        if not follower_with_info['protected']:
            tasks.fetch_follower_last_like_date.delay(self.user_id, follower_with_info)
            tasks.fetch_follower_last_tweet_date.delay(self.user_id, follower_with_info)
        self.twitter_followers_repo.add_follower(follower_with_info)

    def fetch_follower_last_like_date(self, follower_info: dict):
        follower_info['last_like_dt'] = \
            self.twitter_client.fetch_follower_last_like_date(follower_info['twitter_user_id'])
        self.twitter_followers_repo.add_follower(follower_info)
        logger.info(f'Successfully fetched follower named {follower_info["name"]} '
                    f'last like date for user {self.user_id}')

    def fetch_follower_last_tweet_date(self, follower_info: dict):
        follower_info['last_tweet_dt'] = \
            self.twitter_client.fetch_follower_last_tweet_date(follower_info['twitter_user_id'])
        self.twitter_followers_repo.add_follower(follower_info)
        logger.info(f'Successfully fetched follower named {follower_info["name"]} '
                    f'last tweet date for user {self.user_id}')

    def remove_followers(self, params: dict):
        follower_ids_to_remove = get_follower_ids_to_remove(params)
        for follower_id in follower_ids_to_remove:
            tasks.remove_follower.delay(self.user_id, follower_id)

    def remove_follower(self, follower_id):
        self.twitter_client.remove_follower(follower_id)
        self.twitter_followers_repo.remove_follower(follower_id)
        logger.info(f'Removed {len(follower_id)} followers for user {self.user_id}')
