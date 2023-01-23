from twitterAPI.models import TwitterFollower, TwitterUser
from twitterAPI.settings import OBJECTS_PER_PAGE


class TwitterFollowersRepo:
    def __init__(self, twitter_user):
        self.twitter_user = twitter_user

    def fetch_followers(self, currently_following=True, filters=None, order=None,
                        offset=0):
        followers = TwitterFollower.objects.filter(user=self.twitter_user, currently_following=currently_following)
        if filters:
            followers = followers.filter(**filters)
        if order:
            followers = followers.order_by(*order)
        follower_count = followers.count()
        followers = followers[offset: offset + OBJECTS_PER_PAGE]
        return followers, follower_count

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
