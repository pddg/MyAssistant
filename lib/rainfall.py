import json
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
            tweet("\n" + past + "\n" + will, status)
        else:
            name = j['Feature'][0]['Name'].replace('天気', '降雨')
            name = name.replace('地点(135.77705,35.051482)', '松ヶ崎')
            tweet(name + "\n" + past + "\n" + will)


def observation(weather):
    i = 0
    r_f = 0.0
    while 'observation' in weather[i]:
        r_f += weather[i]['Rainfall']
        i += 1
    i += 1
    past_ave = r_f / float(len(weather[0:i]))
    past = ''
    if past_ave == 0.0:
        past = '過去{0}分間に雨は降っていません．'.format(str(10 * i))
    else:
        past = '過去{0}分間の平均降水量は{1}です．'.format(str(10 * i), str(past_ave))
    return past


def forecast(weather):
    i = 0
    while 'observation' in weather[i]:
        print(weather[i]['Rainfall'])
        i += 1
    f = []
    for w in weather[i:]:
        f.append(w['Rainfall'])
    # 昇順に
    f.sort()
    # 降順に
    f.reverse()
    f_c = ""
    # 最初のforecastのDate
    st = weather[i]['Date']
    # 最後のDate
    ed = weather[len(weather) - 1]['Date']
    if f[0] == 0.0:
        f_c = "{0}時{1}分〜{2}時{3}分の間，雨が降る予報はありません.".format(
            st[8:10], st[10:12], ed[8:10], ed[10:12])
    else:
        i = 0.0
        for num in f:
            i += num
        f_c = "{0}時{1}分〜{2}時{3}分にかけて最大{4}mm，平均{5}mm程度の雨が降る予報です．".format(
            st[8:10], st[10:12], ed[8:10], ed[10:12], str(f[0]), str(round(i / float(len(f)), 3)))
    return f_c
