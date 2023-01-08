from twitterAPI.models import TwitterUser


class TwitterUserRepo:
    def __init__(self, user):
        self.user = user
        self._twitter_user = None

    @property
    def twitter_user(self):
        if self._twitter_user is None:
            self._twitter_user = self.fetch_twitter_user()
        return self._twitter_user

    def fetch_twitter_user(self):
        try:
            twitter_user = TwitterUser.objects.get(user=self.user)
        except TwitterUser.DoesNotExist:
            return None
        return twitter_user

    def update_or_create(self, **kwargs):
        twitter_user, created = TwitterUser.objects.update_or_create(user=self.user,
                                                                     defaults=kwargs)
        return twitter_user
