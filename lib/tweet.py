from lib.auth import api
from tweepy.error import TweepError


def tweet(txt, status=None):
    try:
        if status is None:
            api.update_status(status=txt)
        else:
            head = '@' + status.user.screen_name + ' '
            api.update_status(
                status=head + txt, in_reply_to_status_id=status.id)
    except TweepError as e:
        if e.args[0][0]['code'] == 187:
            if status is None:
                pass
            else:
                api.send_direct_message(
                    user_id=status.user.id, text='Status is a duplicate.\n' + txt)
        else:
            raise
    except Exception:
        raise
