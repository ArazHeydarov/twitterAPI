from twitterAPI.utils import CONSUMER_KEY, CONSUMER_SECRET, REQUEST_TOKEN_URL, BASE_OAUTH_URL, ACCESS_TOKEN_URL, \
    SELF_LOOKUP_URL

from requests_oauthlib import OAuth1Session
from twitterAPI.models import TwitterUser


class TwitterClient(object):
    def __init__(self, twitter_user: TwitterUser):
        self.twitter_user = twitter_user

    @staticmethod
    def fetch_authorization_params():
        oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET)

        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        authorization_url = oauth.authorization_url(BASE_OAUTH_URL)

        return authorization_url, resource_owner_key, resource_owner_secret

    @staticmethod
    def fetch_authorization_access_params(resource_owner_key, resource_owner_secret, verifier):
        oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)

        access_token = oauth_tokens.get("oauth_token")
        access_token_secret = oauth_tokens.get("oauth_token_secret")

        return access_token, access_token_secret

    @staticmethod
    def fetch_twitter_user_info(access_token, access_token_secret):
        info_scope = "id,name"
        params = {"user.fields": info_scope}
        oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        response = oauth.get(SELF_LOOKUP_URL, params=params)

        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )
        data = response.json().get("data")
        return data.get('id'), data.get('name')

    def fetch_followers_list(self):
        oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=self.twitter_user.access_token,
            resource_owner_secret=self.twitter_user.access_token_secret,
        )

        request_url = f"https://api.twitter.com/2/users/{self.twitter_user.twitter_user_id}/followers"
        followers = oauth.get(request_url).json().get("data")
        return followers

