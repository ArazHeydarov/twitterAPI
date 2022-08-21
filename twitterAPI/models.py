from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class TwitterUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    resource_owner_key = models.CharField(max_length=256, null=False)
    resource_owner_secret = models.CharField(max_length=256, null=False)
    access_token = models.CharField(max_length=256)
    access_token_secret = models.CharField(max_length=256)
    twitter_user_id = models.IntegerField(null=True)
    twitter_user_name = models.CharField(max_length=256)

    def __str__(self):
        return self.user.username


class TwitterFollower(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    twitter_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    pp_url = models.CharField(max_length=512)
    protected = models.BooleanField()
    last_like_dt = models.DateTimeField(null=True)
    last_tweet_dt = models.DateTimeField(null=True)
    currently_following = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
