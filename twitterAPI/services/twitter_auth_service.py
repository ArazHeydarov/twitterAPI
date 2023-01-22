from twitterAPI.clients.twitter_client import TwitterClient
from twitterAPI.repos.twitter_user_repo import TwitterUserRepo


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
