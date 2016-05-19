import urllib.request as request
from datetime import datetime, timedelta
import json
from lib.auth import api
from lib.rainfall import get_weather


def get_json():
    try:
        base_url = "http://weather.livedoor.com/forecast/webservice/json/v1?city="
        city_id = "260010"
        r = request.urlopen(base_url + city_id)
        return json.loads(r.read().decode('utf-8'))
    except Exception:
        return False


def parse_forecast_auto():
    j = get_json()
    if j is False:
        return False
    desc = j['description']['text'].strip().replace('\n', '')
    d = datetime.now()
    if 16 < d.hour <= 24:
        # 明日の天気
        d += timedelta(days=1)
    f = parse_date(j['forecasts'], d.strftime("%Y-%m-%d"))
    return [f['dateLabel'], j['title'], f['telop'],
            f['temperature']['max']['celsius'],
            f['temperature']['min']['celsius'], desc,
            j['link']]


def parse_date(fc_list, date):
    result = {}
    for f in fc_list:
        if date == f['date']:
            result = f
        else:
            pass
    return result


def return_weather_auto(status=None):
    forecast = parse_forecast_auto()
    t = "{0}の{1}は{2}．max:{3}度，min:{4}度\n{5}".format(*forecast[0:6])
    if len(t) > 103:
        num = len(t) - 103
        forecast[5] = forecast[5][:-num]
    t = "{0}の{1}は{2}．max:{3}度，min:{4}度\n{5}".format(
        *forecast[0:6]) + ' ' + forecast[6]
    if status is not None:
        head = '@' + status.user.screen_name + ' '
        api.update_status(status=head + t, in_reply_to_status_id=status.id)
    else:
        api.update_status(status=t)
        if forecast[2] is not '晴れ':
            get_weather()

if __name__ == "__main__":
    return_weather_auto()
