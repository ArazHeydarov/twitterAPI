from twitterAPI.clients import TwitterClient
from twitterAPI.repo import TwitterUserRepo, TwitterFollowersRepo
from twitterAPI.models import User
from twitterAPI.utils import process_profile_picture, get_follower_ids_to_remove


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
    def __init__(self, user: User):
        self.user = user
        self.twitter_user_repo = TwitterUserRepo(user)
        self.twitter_user = self.twitter_user_repo.fetch_twitter_user()
        self.twitter_client = TwitterClient(self.twitter_user)
        self.twitter_followers_repo = TwitterFollowersRepo(self.twitter_user)

    def get_followers(self):
        return self.twitter_followers_repo.fetch_followers()

    def update_followers(self):
        followers_list = self.get_follower_list()
        followers_with_info = [self.get_followers_info(follower) for follower in followers_list]
        self.twitter_followers_repo.add_followers(followers_with_info)
        return followers_list

    def get_follower_list(self):
        return self.twitter_client.fetch_followers_list()

    def get_followers_info(self, follower: dict):
        pp_url, protected = self.twitter_client.fetch_follower_basic_info(follower['id'])
        pp_url = process_profile_picture(pp_url)
        follower_with_info = {'twitter_user_id': follower['id'],
                              'name': follower['name'],
                              'username': follower['username'],
                              'pp_url': pp_url,
                              'protected': protected}

        if not follower_with_info['protected']:
            follower_with_info['last_like_dt'] = self.twitter_client.fetch_follower_last_like_date(follower['id'])
            follower_with_info['last_tweet_dt'] = self.twitter_client.fetch_follower_last_tweet_date(follower['id'])
        return follower_with_info

    def remove_followers(self, params: dict):
        follower_ids_to_remove = get_follower_ids_to_remove(params)
        for follower_id in follower_ids_to_remove:
            self.twitter_client.remove_follower(follower_id)
            self.twitter_followers_repo.remove_follower(follower_id)
