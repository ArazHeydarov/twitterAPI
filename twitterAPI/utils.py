import os
from .models import TwitterUser, TwitterFollower

CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
BASE_OAUTH_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
SELF_LOOKUP_URL = "https://api.twitter.com/2/users/me"


def process_profile_picture(pp_url: str):
    if pp_url:
        return pp_url.replace("_normal", "")


def get_follower_ids_to_remove(post_dictionary):
    ids_to_remove = []
    for key, value in post_dictionary.items():
        if key[:3] == 'uid' and value == 'on':
            _, _, follower_id = key.partition('_')
            ids_to_remove.append(follower_id)
    return ids_to_remove


