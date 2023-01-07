import asyncio
import json
import os

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from requests_oauthlib import OAuth1Session

from .models import TwitterUser, TwitterFollower

import twitterAPI.twitter_utils as tu


def twitter_connection(user):
    return hasattr(user, 'twitteruser') and user.twitteruser.access_token_secret


@login_required
def twitter(request):
    twitter_user = tu.check_if_twitter_user_exist(request.user)

    if not twitter_user:
        authorization_url, resource_owner_key, resource_owner_secret = tu.get_authorization_url()

        t = TwitterUser(user=request.user, resource_owner_key=resource_owner_key,
                        resource_owner_secret=resource_owner_secret)
        t.save()
        return render(request, 'twitter.html', {'authorization_url': authorization_url})
    return redirect('twitter_followers')


def index(request):
    if request.user.is_authenticated:
        return redirect(to=twitter)
    return render(request, 'index.html')


@login_required
def verify(request):
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")

    twitter_user = request.user.twitteruser
    resource_owner_key = twitter_user.resource_owner_key
    resource_owner_secret = twitter_user.resource_owner_secret

    verifier = request.GET.get('oauth_verifier')
    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    twitter_user.access_token = access_token
    twitter_user.access_token_secret = access_token_secret
    twitter_user.save()

    return redirect('twitter_signin')


@login_required
@user_passes_test(twitter_connection, redirect_field_name='twitter_signin')
def twitter_followers(request):
    if request.method == 'POST':
        requester = request.user.twitteruser
        ids_to_remove = tu.get_follower_ids_to_remove(request.POST)
        # tu.remove_follower(requester, ids_to_remove)
        return HttpResponse("Success")

    twitter_user = request.user.twitteruser
    if not twitter_user.twitter_user_id:
        tu.get_assign_twitter_user_id(twitter_user)
    followers = request.user.twitterfollower_set.all()

    return render(request, 'twitter_followers.html', {'followers': followers})


@require_http_methods(['GET'])
@login_required
@user_passes_test(twitter_connection, redirect_field_name='twitter_signin')
async def update_twitter_followers(request):
    asyncio.create_task(update(request))
    return redirect('twitter_followers')


async def update(request):
    print('Bla bla bla bla')
    request.user.twitterfollower_set.all().update(currently_following=False)

    followers = tu.get_followers(requester=request.user.twitteruser)
    followers = tu.get_extra_user_info(requester=request.user.twitteruser, users=followers)
    for follower in followers:
        existing_follower = request.user.twitterfollower_set.filter(twitter_id=follower['twitter_id'])
        if existing_follower:
            existing_follower.update(currently_following=True, **follower)
        else:
            tf = TwitterFollower(user=request.user, currently_following=True, **follower)
            tf.save()
