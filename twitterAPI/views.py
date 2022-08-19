import json
import os

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from requests_oauthlib import OAuth1Session

from .models import TwitterUser

import twitterAPI.twitter_utils as tu


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

    return redirect('twitter_signin')


@login_required
def twitter_followers(request):
    if request.method == 'POST':
        requester = request.user.twitteruser
        ids_to_remove = tu.get_follower_ids_to_remove(request.POST)
        # tu.remove_follower(requester, ids_to_remove)
        return HttpResponse("Success")

    if not hasattr(request.user, 'twitteruser') or not request.user.twitteruser.access_token_secret:
        return HttpResponseForbidden()
    twitter_user = request.user.twitteruser
    if not twitter_user.twitter_user_id:
        tu.get_assign_twitter_user_id(twitter_user)
    # oauth = tu.get_oauth_session(twitter_user)
    #
    # request_url = f"https://api.twitter.com/2/users/{twitter_user.twitter_user_id}/followers"
    # response = oauth.get(request_url)
    # response = response.json()
    data = [{'id': '1511659535940960257', 'name': 'sahilə.', 'username': 'sahilacabbar_'},
     {'id': '925806316664344576', 'name': 'Kreisleriann', 'username': 'kreisleriann'},
     {'id': '1535594492304457730', 'name': 'Mena', 'username': 'Marshal19679935'},
     {'id': '1316335608416145408', 'name': 'd 503', 'username': 'No_hellbelowus'},
     {'id': '822500826702839809', 'name': 'a_sad_aylin', 'username': 'AsadovaAylin'},
     {'id': '1536667028035096576', 'name': 'Nezzy', 'username': 'Nezzyy981'},
     {'id': '606544269', 'name': 'nijat', 'username': 'nijatRz'},
     {'id': '23309401', 'name': 'Türkel99', 'username': 'schimanski99'},
     {'id': '1503382763298299909', 'name': '59.748 aztwi anı', 'username': 'canliaztwi'},
     {'id': '95704214', 'name': 'Nesir Имишлили', 'username': 'nesir91'},
     {'id': '1080740420139843584', 'name': 'Leyla', 'username': 'lylagua'},
     {'id': '1062118918649769984', 'name': 'Call me Nadia', 'username': 'belalicivciv0'},
     {'id': '541100376', 'name': 'Ali Almas', 'username': 'alialmasli'},
     {'id': '966393467319484417', 'name': 'Slmtal', 'username': 'Salimatalibli'},
     {'id': '2338475239', 'name': 'İlhamə', 'username': 'ilhamammadova'},
     {'id': '1485259412944134148', 'name': 'ayshan', 'username': 'kmvayshn'},
     {'id': '802434246598152192', 'name': 'anita', 'username': 'cvetnayabumaqa'},
     {'id': '1221045856679448577', 'name': 'Uchiha Pasha', 'username': 'UPasavage'},
     {'id': '1315292794370625539', 'name': 'Elnarə Cəfər', 'username': 'lnrcfrv'},
     {'id': '1438268966732959755', 'name': 'маша каша', 'username': 'titainnn'},
     {'id': '1201966927830237184', 'name': 'Arzu', 'username': 'ArzuHjyva'},
     {'id': '4264151398', 'name': 'the day Lady Lazarus died', 'username': 'Aytac_hac'}]
    return render(request, 'twitter_followers.html', {'followers': data})
