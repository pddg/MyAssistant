import json
from datetime import datetime
import urllib.request as request
import urllib.parse as parse
from lib.settings import myapp
from lib.tweet import tweet


def get_weather(status=None):
    base_url = "http://weather.olp.yahooapis.jp/v1/place?"
    params = parse.urlencode({"coordinates": "135.777046,35.051482",
                              "appid": myapp,
                              "output": 'json'})
    response = request.urlopen(base_url + params)
    j = json.loads(response.read().decode('utf-8'))
    if 'Error' in j:
        if status is not None:
            tweet("APIサーバがダウンしています．", status)
        else:
            tweet("Yahooの気象情報APIサーバがダウンしています．")
    else:
        weather = j['Feature'][0]['Property']['WeatherList']['Weather']
        past = observation(weather)
        will = forecast(weather)
        if status is not None:
            tweet(past + "\n" + will, status)
        else:
            tweet(past + "\n" + will)


def observation(weather):
    ob = [r for r in weather if r['Type'] == "observation"]
    ob_rain = [r['Rainfall'] for r in ob]
    past_min = str(10 * (len(ob_rain)))
    if sum(ob_rain) == 0.0:
        past = '過去{0}分間に雨は降っていません．'.format(past_min)
    else:
        ave = round(sum(ob_rain) / float(len(ob_rain)), 1)
        past = '過去{0}分間の平均降水量は{1}mmです．'.format(past_min, str(ave))
    return past


def forecast(weather):
    fo = [r for r in weather if r['Type'] == "forecast"]
    # 最初のforecastのDate
    st = fo[0]['Date']
    # 最後のDate
    ed = fo[len(fo) - 1]['Date']
    fo_rain = [r['Rainfall'] for r in fo]
    # 昇順に
    fo_rain.sort()
    # 逆に(値の小さい順に)
    fo_rain.reverse()
    if fo_rain[0] == 0.0:
        f_c = "{0}時{1}分〜{2}時{3}分の間，雨が降る予報はありません.".format(
            st[8:10], st[10:12], ed[8:10], ed[10:12])
    else:
        fo_rain_sum = sum(fo_rain)
        each_rain = ""
        for f in fo:
            time = datetime.strptime(f['Date'], "%Y%m%d%H%M")
            each = "{date} {rain}\n".format(date=time.strftime('%H:%M'), rain=f['Rainfall'])
            each_rain += each
        f_c = each_rain + "平均{}mm程度の雨が降る予報です．".format(str(round(fo_rain_sum / float(len(fo_rain)), 3)))
    return f_c
