import os

from requests_oauthlib import OAuth1Session

from .models import TwitterUser


def check_if_twitter_user_exist(user):
    try:
        twitter_user = user.twitteruser
        if not twitter_user.access_token or not twitter_user.access_token_secret:
            twitter_user.delete()
            twitter_user = None
    except TwitterUser.DoesNotExist:
        twitter_user = None
    return twitter_user


def get_authorization_url():
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

    return authorization_url, resource_owner_key, resource_owner_secret


def get_oauth_session(twitter_user):
    # Make the request
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")

    access_token = twitter_user.access_token
    access_token_secret = twitter_user.access_token_secret

    return OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )


def get_assign_twitter_user_id(twitter_user):
    fields = "id,name"
    params = {"user.fields": fields}

    oauth = get_oauth_session(twitter_user)

    response = oauth.get("https://api.twitter.com/2/users/me", params=params)

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )
    json_response = response.json()
    twitter_user.twitter_user_id = json_response['data']['id']
    twitter_user.twitter_user_name = json_response['data']['name']
    twitter_user.save()


def get_follower_ids_to_remove(post_dictionary):
    ids_to_remove = []
    for key, value in post_dictionary.items():
        if key[:3] == 'uid' and value == 'on':
            _, _, follower_id = key.partition('_')
            ids_to_remove.append(follower_id)
    return ids_to_remove


def remove_follower(requester, ids_to_remove):
    oauth = get_oauth_session(requester)
    for follower_id in ids_to_remove:
        block_url = f"https://api.twitter.com/2/users/{requester.twitter_user_id}/blocking"
        response = oauth.post(block_url, json={"target_user_id": f"{follower_id}"})
        unblock_url = f"https://api.twitter.com/2/users/{requester.twitter_user_id}/blocking/{follower_id}"
        response = oauth.delete(unblock_url)

