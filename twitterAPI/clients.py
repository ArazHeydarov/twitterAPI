from twitterAPI.utils import CONSUMER_KEY, CONSUMER_SECRET, REQUEST_TOKEN_URL, BASE_OAUTH_URL, ACCESS_TOKEN_URL

from requests_oauthlib import OAuth1Session


class TwitterClient(object):
    def __init__(self, twitter_user=None):
        pass

    @staticmethod
    def get_authorization_params():
        oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET)

        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        authorization_url = oauth.authorization_url(BASE_OAUTH_URL)

        return authorization_url, resource_owner_key, resource_owner_secret

    @staticmethod
    def get_authorization_access_params(resource_owner_key, resource_owner_secret, verifier):
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
