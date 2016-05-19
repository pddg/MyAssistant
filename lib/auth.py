import tweepy
import lib.settings as settings


auth = tweepy.OAuthHandler(settings.CK, settings.CS)
auth.set_access_token(settings.AT, settings.AS)
api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True)
