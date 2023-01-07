from twitterAPI.models import TwitterUser


class TwitterUserRepo:
    def __init__(self, user):
        self.user = user
        self._twitter_user = None

    @property
    def twitter_user(self):
        if self._twitter_user is None:
            self._twitter_user = self.check_oauth_authorization(self.user)
        return self._twitter_user

    @staticmethod
    def check_oauth_authorization(user):
        try:
            twitter_user = TwitterUser.objects.get(user=user)
        except TwitterUser.DoesNotExist:
            return None

        if not twitter_user.access_token or not twitter_user.access_token_secret:
            twitter_user.delete()
            twitter_user = None
        return twitter_user

    def create(self, resource_owner_key, resource_owner_secret):
        twitter_user = TwitterUser(user=self.user, resource_owner_key=resource_owner_key,
                                   resource_owner_secret=resource_owner_secret)
        twitter_user.save()
        return twitter_user

