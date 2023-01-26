import math
import logging
from twitterAPI.repos.twitter_user_repo import TwitterUserRepo
from twitterAPI.repos.twitter_follower_repo import TwitterFollowersRepo
from twitterAPI.clients.twitter_client import TwitterClient
import twitterAPI.tasks as tasks
from twitterAPI.utils import process_profile_picture, get_follower_ids_to_remove
from twitterAPI.settings import OBJECTS_PER_PAGE

logger = logging.getLogger('services')


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
        followers, follower_count = self.twitter_followers_repo.fetch_followers(currently_following=True,
                                                                                filters=filters,
                                                                                order=order, offset=offset)
        page_numbers = [index for index in range(2, math.ceil(follower_count / OBJECTS_PER_PAGE) + 1)]
        logger.info(f'Fetched {follower_count} followers for user {self.user_id}')
        return followers, page_numbers,

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

    def fetch_follower_basic_info(self, follower_info: dict):
        logger.info(f'Fetching follower named {follower_info["name"]} basic info for user {self.user_id}')
        pp_url, protected = self.twitter_client.fetch_follower_basic_info(follower_info['id'])
        pp_url = process_profile_picture(pp_url)
        follower_with_info = {'twitter_user_id': follower_info['id'],
                              'name': follower_info['name'],
                              'username': follower_info['username'],
                              'pp_url': pp_url,
                              'protected': protected}
        if not protected:
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
            self.twitter_client.remove_follower(follower_id)
            self.twitter_followers_repo.remove_follower(follower_id)
        logger.info(f'Removed {len(follower_ids_to_remove)} followers for user {self.user_id}')
