from twitterAPI.clients import TwitterClient
from twitterAPI.repo import TwitterUserRepo


class TwitterAuthService:
    def __init__(self, user):
        self.user = user
        self.twitter_client = TwitterClient(user)
        self.twitter_user_repo = TwitterUserRepo(user)
        self._authorization_url = None
        self._resource_owner_key = None
        self._resource_owner_secret = None

    def _get_authorization_params(self):
        self._authorization_url, self._resource_owner_key, self._resource_owner_secret = \
            self.twitter_client.get_authorization_params()

    def _bind_user_to_twitter_user(self):
        self.twitter_user_repo.create(resource_owner_key=self._resource_owner_key,
                                      resource_owner_secret=self._resource_owner_secret)

    @property
    def authorization_url(self):
        if not self._authorization_url:
            self._get_authorization_params()
            self._bind_user_to_twitter_user()
        return self._authorization_url
