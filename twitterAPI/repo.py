from twitterAPI.models import TwitterUser, TwitterFollower


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

    @staticmethod
    def fetch_twitter_user_by_id(user_id):
        try:
            twitter_user = TwitterUser.objects.get(user_id=user_id)
        except TwitterUser.DoesNotExist:
            return None
        return twitter_user

    def update_or_create(self, **kwargs):
        twitter_user, created = TwitterUser.objects.update_or_create(user=self.user,
                                                                     defaults=kwargs)
        return twitter_user


class TwitterFollowersRepo:
    def __init__(self, twitter_user):
        self.twitter_user = twitter_user

    def fetch_followers(self, currently_following=True):
        followers = TwitterFollower.objects.filter(user=self.twitter_user, currently_following=currently_following)
        return followers

    def add_follower(self, follower):
        follower['user'] = self.twitter_user
        follower['currently_following'] = True
        TwitterFollower.objects.update_or_create(defaults=follower, user=self.twitter_user,
                                                 twitter_user_id=follower['twitter_user_id'])

    def remove_follower(self, follower_id):
        try:
            twitter_follower = TwitterFollower.objects.get(user=self.twitter_user, twitter_user_id=follower_id)
            twitter_follower.currently_following = False
            twitter_follower.save()
        except TwitterUser.DoesNotExist:
            return

    def update_followers_following_status(self):
        TwitterFollower.objects.filter(user=self.twitter_user).update(currently_following=False)



