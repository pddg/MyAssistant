import urllib.request as request
from datetime import datetime, timedelta
import json
from lib.rainfall import get_weather
from lib.tweet import tweet


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
    max_temp = f['temperature']['max']
    min_temp = f['temperature']['min']
    if max_temp is not None:
        max_temp = max_temp['celsius']
    if min_temp is not None:
        min_temp = min_temp['celsius']
    return {"date": f['dateLabel'], "title": j['title'], "telop": f['telop'],
            "max": max_temp, "min": min_temp, "desc": desc, "link": j['link']}


def parse_date(fc_list, date):
    result = {}
    for f in fc_list:
        if date == f['date']:
            result = f
        else:
            pass
    return result


def return_weather_auto(status=None):
    f = parse_forecast_auto()
    max_t = ""
    min_t = ""
    if f["min"] is not None:
        min_t = " min:{0}度,".format(f['min'])
    if f["max"] is not None:
        max_t = " max:{0}度,".format(f["max"])
    t = "{0}の{1}は{2}".format(
        f["date"], f["title"], f["telop"]) + max_t + min_t + "\n"
    if len(t + f['desc']) > 103:
        num = len(t + f["desc"]) - 103
        f["desc"] = f["desc"][:-num]
    t = t + f["desc"]
    if status is not None:
        tweet(t, status)
    else:
        tweet(t)
        if "晴れ" not in f["telop"]:
            get_weather()

if __name__ == "__main__":
    return_weather_auto()
