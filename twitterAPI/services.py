from twitterAPI.clients import TwitterClient
from twitterAPI.repo import TwitterUserRepo, TwitterFollowersRepo
from twitterAPI.utils import process_profile_picture, get_follower_ids_to_remove
import twitterAPI.tasks as tasks


class TwitterAuthService:
    def __init__(self, user):
        self.user = user
        self.twitter_user_repo = TwitterUserRepo(user)

    def get_authorization_url(self):
        authorization_url, resource_owner_key, resource_owner_secret = TwitterClient.fetch_authorization_params()
        self.save_params(resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret)
        return authorization_url

    def _get_authorization_params(self):
        self._authorization_url, self._resource_owner_key, self._resource_owner_secret = \
            TwitterClient.fetch_authorization_params()

    def get_twitter_user(self):
        return self.twitter_user_repo.fetch_twitter_user()

    def save_params(self, **kwargs):
        twitter_user = self.twitter_user_repo.update_or_create(**kwargs)
        return twitter_user

    def validate_oauth_authorization(self):
        twitter_user = self.twitter_user_repo.fetch_twitter_user()
        if twitter_user and twitter_user.access_token and twitter_user.access_token_secret:
            return True
        return False

    def validate_pending_verification(self):
        twitter_user = self.twitter_user_repo.fetch_twitter_user()
        if twitter_user and twitter_user.resource_owner_key and twitter_user.resource_owner_secret:
            return True
        return False

    def verify_oauth_token(self, oauth_verifier):
        twitter_user = self.twitter_user_repo.fetch_twitter_user()
        access_token, access_token_secret = TwitterClient.fetch_authorization_access_params(
            twitter_user.resource_owner_key, twitter_user.resource_owner_secret, oauth_verifier
        )
        twitter_id, twitter_name = TwitterClient.fetch_twitter_user_info(access_token, access_token_secret)
        self.save_params(access_token=access_token, access_token_secret=access_token_secret,
                         twitter_user_id=twitter_id, twitter_user_name=twitter_name)


class TwitterFollowerService:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.twitter_user = TwitterUserRepo.fetch_twitter_user_by_id(self.user_id)
        self.twitter_client = TwitterClient(self.twitter_user)
        self.twitter_followers_repo = TwitterFollowersRepo(self.twitter_user)

    def get_followers(self):
        return self.twitter_followers_repo.fetch_followers(currently_following=True)

    def update_followers(self):
        self.twitter_followers_repo.update_followers_following_status()
        tasks.fetch_follower_ids.delay(self.user_id)

    def fetch_follower_list(self):
        follower_list = self.twitter_client.fetch_followers_list()
        for follower in follower_list:
            tasks.fetch_follower_basic_info.delay(self.user_id, follower)

    def fetch_follower_basic_info(self, follower_info: dict):
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

    def fetch_follower_last_tweet_date(self, follower_info: dict):
        follower_info['last_tweet_dt'] = \
            self.twitter_client.fetch_follower_last_tweet_date(follower_info['twitter_user_id'])
        self.twitter_followers_repo.add_follower(follower_info)

    def remove_followers(self, params: dict):
        follower_ids_to_remove = get_follower_ids_to_remove(params)
        for follower_id in follower_ids_to_remove:
            self.twitter_client.remove_follower(follower_id)
            self.twitter_followers_repo.remove_follower(follower_id)
