import tweepy
import time
import re
import lib.settings as settings
from threading import Thread
from lib.auth import api, auth
from lib.mention_action import return_cancel, return_info, return_info_by_id
from lib.rainfall import get_weather
from lib.weather import return_weather_auto

mydata = api.me()
myid = mydata.id


class StreamError(Exception):

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return ('Receive Error Code: '.format(self.status))


class Listener(tweepy.streaming.StreamListener):

    def __init__(self, queue):
        super(Listener, self).__init__()
        self.queue = queue

    def on_status(self, status):
        if status.in_reply_to_user_id == myid:
            self.queue.put(status)
        else:
            pass

    def on_error(self, status):
        raise StreamError(status)


class StreamRecieverThread(Thread):

    def __init__(self, queue):
        super(StreamRecieverThread, self).__init__()
        self.daemon = True
        self.queue = queue

    def run(self):
        l = Listener(self.queue)
        stream = tweepy.Stream(auth, l)
        while True:
            try:
                stream.userstream()
            except Exception:
                time.sleep(60)
                stream = tweepy.Stream(auth, l)


def tweetassembler(status):
    try:
        from_user = status.user
        if from_user.id in settings.my_accounts:
            r = re.compile(".*休.*")
            if re.match(r, status.text):
                return_cancel(status)
            r = re.compile(".*連絡.*")
            if re.match(r, status.text):
                return_info(status)
            r = re.compile('@\S*\s[0-9]+')
            if re.match(r, status.text):
                return_info_by_id(status)
            r = re.compile(".*雨.*")
            if re.match(r, status.text):
                get_weather(status)
            r = re.compile(".*天気.*")
            if re.match(r, status.text):
                return_weather_auto(status)
    except Exception:
        raise
