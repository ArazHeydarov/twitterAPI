import asyncio
import json
import os

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from requests_oauthlib import OAuth1Session

from .models import TwitterUser, TwitterFollower

import twitterAPI.utils as tu
from twitterAPI.repo import TwitterUserRepo
from twitterAPI.services import TwitterAuthService


@login_required(login_url='/signin')
@user_passes_test(TwitterUserRepo.check_oauth_authorization, login_url='twitter_auth')
def dashboard(request):
    user = request.user
    repo = TwitterUserRepo(user)
    oauth_credentials = repo.twitter_user

    if not oauth_credentials:
        return redirect(to='twitter_auth')
    return HttpResponse('Dashboard')


@login_required(login_url='/signin')
def twitter_auth(request):
    user = request.user
    if TwitterUserRepo.check_oauth_authorization(user):
        return redirect('dashboard')
    auth_service = TwitterAuthService(user)
    twitter_auth_url = auth_service.authorization_url
    return render(request, 'twitter.html', {'authorization_url': twitter_auth_url})


def index(request):
    if request.user.is_authenticated:
        return redirect(to='dashboard')
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
@user_passes_test(TwitterUserRepo.check_oauth_authorization, redirect_field_name='twitter_auth')
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
@user_passes_test(TwitterUserRepo.check_oauth_authorization, redirect_field_name='twitter_auth')
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
