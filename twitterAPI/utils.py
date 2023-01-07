import os
from .models import TwitterUser, TwitterFollower

CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
BASE_OAUTH_URL = "https://api.twitter.com/oauth/authorize"




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


def get_followers(requester: TwitterUser):
    oauth = get_oauth_session(requester)

    request_url = f"https://api.twitter.com/2/users/{requester.twitter_user_id}/followers"
    response = oauth.get(request_url)
    response = response.json()
    followers = response['data']
    return followers


def get_extra_user_info(requester, users):
    oauth = get_oauth_session(requester)
    fields = "profile_image_url,protected"
    params = {"user.fields": fields}
    extra_users_info = users.copy()
    for user in extra_users_info:
        user['twitter_id'] = user['id']
        del user['id']
        user_id = user['twitter_id']

        # getting profile picture
        profile_url = f"https://api.twitter.com/2/users/{user_id}"
        profile_response = oauth.get(url=profile_url, params=params)
        if profile_response.status_code == 200:
            profile_json_response = profile_response.json()
            profile_user_data = profile_json_response['data']
            user['pp_url'] = profile_user_data['profile_image_url']
            user['protected'] = profile_user_data['protected']

        if user.get('protected'):
            continue
        # getting last tweet
        last_tweet_params = {'exclude': 'replies', 'max_results': 5,
                             'tweet.fields': 'created_at'}
        last_tweet_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        last_tweet_response = oauth.get(url=last_tweet_url, params=last_tweet_params)
        if last_tweet_response.status_code == 200:
            last_tweet_json_response = last_tweet_response.json()
            last_tweet_data = last_tweet_json_response.get('data')
            if last_tweet_data:
                last_tweet_data = last_tweet_data[0]
                user['last_tweet_dt'] = last_tweet_data.get('created_at')
            else:
                user['last_tweet_dt'] = None

        # getting last like
        last_like_params = {'max_results': 10, 'tweet.fields': 'created_at'}
        last_like_url = f'https://api.twitter.com/2/users/{user_id}/liked_tweets'
        last_like_response = oauth.get(url=last_like_url, params=last_like_params)
        if last_like_response.status_code == 200:
            last_like_json_response = last_like_response.json()
            last_like_data = last_like_json_response.get('data')
            if last_like_data:
                last_like_data = last_like_data[0]
                user['last_like_dt'] = last_like_data['created_at']
            else:
                user['last_like_dt'] = None
    return extra_users_info
