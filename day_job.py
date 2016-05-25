from datetime import datetime
from lib.weather import return_weather_auto
from lib.mention_action import get_today_cancel, get_today_info
from lib.tweet import tweet


def day_job():
    try:
        return_weather_auto()
        d = datetime.now()
        if 16 < d.hour <= 24:
            pass
        else:
            tweet(get_today_cancel(d))
            tweet(get_today_info())
    except Exception:
        raise


if __name__ == "__main__":
    day_job()
