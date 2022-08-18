import os

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TwitterUser

from requests_oauthlib import OAuth1Session


@login_required
def twitter(request):
    try:
        twitter_user = request.user.twitteruser
        if not twitter_user.access_token or not twitter_user.access_token_secret:
            twitter_user.delete()
            twitter_user = None
    except TwitterUser.DoesNotExist:
        twitter_user = None

    if not twitter_user:
        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get("CONSUMER_SECRET")

        # Get request token
        request_token_url = "https://api.twitter.com/oauth/request_token"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        fetch_response = oauth.fetch_request_token(request_token_url)
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        t = TwitterUser(user=request.user, resource_owner_key=resource_owner_key,
                        resource_owner_secret=resource_owner_secret)
        t.save()
        return render(request, 'twitter.html', {'authorization_url': authorization_url})
    return HttpResponse('Success')


def index(request):
    if request.user.is_authenticated:
        return redirect(to=twitter)
    return render(request, 'index.html')


def signin(request):
    if request.user.is_authenticated:
        return redirect(to='index')

    if request.method == 'GET':
        return render(request, 'signin.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
            else:
                return render(request, 'signin.html', {'warning_message': 'Credentials are wrong'})

        return redirect(to='index')


def sign_out(request):
    logout(request)
    return redirect(to='index')


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

    return redirect(index)
