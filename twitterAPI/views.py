import asyncio


from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from requests_oauthlib import OAuth1Session

from .models import TwitterUser, TwitterFollower

import twitterAPI.utils as tu
from twitterAPI.services import TwitterAuthService, TwitterFollowerService


@login_required()
def dashboard(request):
    user = request.user
    auth_service = TwitterAuthService(user)

    if not auth_service.validate_oauth_authorization():
        return redirect(to='twitter_auth')

    followers = TwitterFollowerService(user).get_followers()
    return render(request, 'tw_dashboard.html', {'followers': followers})


@login_required()
def twitter_auth(request):
    user = request.user
    auth_service = TwitterAuthService(user)
    if auth_service.validate_oauth_authorization():
        return redirect('dashboard')
    twitter_auth_url = auth_service.get_authorization_url()
    return render(request, 'tw_signin.html', {'authorization_url': twitter_auth_url})


def index(request):
    if request.user.is_authenticated:
        return redirect(to='dashboard')
    return render(request, 'index.html')


@login_required()
def verify(request):
    user = request.user
    auth_service = TwitterAuthService(user)
    if not auth_service.validate_pending_verification():
        return redirect(to='twitter_auth')

    oauth_verifier = request.GET.get('oauth_verifier')
    auth_service.verify_oauth_token(oauth_verifier)
    return redirect('dashboard')


@login_required
def twitter_followers(request):
    user = request.user
    auth_service = TwitterAuthService(user)

    if not auth_service.validate_oauth_authorization():
        return redirect(to='twitter_auth')
    if request.method == 'POST':
        requester = request.user.twitteruser
        ids_to_remove = tu.get_follower_ids_to_remove(request.POST)
        # tu.remove_follower(requester, ids_to_remove)
        return HttpResponse("Success")

    twitter_user = request.user.twitteruser
    if not twitter_user.twitter_user_id:
        tu.get_assign_twitter_user_id(twitter_user)
    followers = request.user.twitterfollower_set.all()

    return render(request, 'tw_dashboard.html', {'followers': followers})


@require_http_methods(['GET'])
@login_required
def update_twitter_followers(request):
    user = request.user
    if not TwitterAuthService(user).validate_oauth_authorization():
        return redirect(to='twitter_auth')

    TwitterFollowerService(user).update_followers()
    return redirect('dashboard')


@require_http_methods(['POST'])
@login_required
def remove_twitter_followers(request):
    user = request.user
    if not TwitterAuthService(user).validate_oauth_authorization():
        return redirect(to='twitter_auth')

    TwitterFollowerService(user).remove_followers(request.POST.dict())
    return redirect('dashboard')



