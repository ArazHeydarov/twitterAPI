import os
from .models import TwitterUser, TwitterFollower

CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
BASE_OAUTH_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
SELF_LOOKUP_URL = "https://api.twitter.com/2/users/me"


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






