from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from twitterAPI.services.twitter_auth_service import TwitterAuthService
from twitterAPI.services.twitter_follower_service import TwitterFollowerService


def index(request):
    if request.user.is_authenticated:
        return redirect(to='dashboard')
    return render(request, 'index.html')


@login_required()
def dashboard(request):
    user = request.user
    auth_service = TwitterAuthService(user)

    if not auth_service.validate_oauth_authorization():
        return redirect(to='twitter_auth')
    request_params = request.GET
    followers, page_numbers = TwitterFollowerService(user.id).get_followers(request_params)
    return render(request, 'tw_dashboard.html', {'followers': followers, 'page_numbers': page_numbers,
                                                 'request_params': request_params})


@login_required()
def twitter_auth(request):
    user = request.user
    auth_service = TwitterAuthService(user)
    if auth_service.validate_oauth_authorization():
        return redirect('dashboard')
    twitter_auth_url = auth_service.get_authorization_url()
    return render(request, 'tw_signin.html', {'authorization_url': twitter_auth_url})


@login_required()
def verify(request):
    user = request.user
    auth_service = TwitterAuthService(user)
    if not auth_service.validate_pending_verification():
        return redirect(to='twitter_auth')

    oauth_verifier = request.GET.get('oauth_verifier')
    auth_service.verify_oauth_token(oauth_verifier)
    return redirect('dashboard')


@require_http_methods(['GET'])
@login_required
def update_twitter_followers(request):
    user = request.user
    if not TwitterAuthService(user).validate_oauth_authorization():
        return redirect(to='twitter_auth')

    TwitterFollowerService(user.id).update_followers()
    return redirect('dashboard')


@require_http_methods(['POST'])
@login_required
def remove_twitter_followers(request):
    user = request.user
    if not TwitterAuthService(user).validate_oauth_authorization():
        return redirect(to='twitter_auth')

    TwitterFollowerService(user.id).remove_followers(request.POST.dict())
    return redirect('dashboard')



