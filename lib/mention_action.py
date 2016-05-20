from datetime import datetime, timedelta
import re
from sqlalchemy import text
from lib.session import Session
from lib.models import Cancel, Info
from lib.settings import my_subjects
from lib.auth import api


def judge_date(text):
    d = datetime.now()
    if '今日' in text or 'きょう' in text:
        return '{0}/{1}/{2}'.format(d.year, d.month, d.day)
    elif '明日' in text or 'あした' in text:
        d = d + timedelta(days=1)
        return '{0}/{1}/{2}'.format(d.year, d.month, d.day)
    elif '明後日' in text or 'あさって' in text:
        d = d + timedelta(days=2)
        return '{0}/{1}/{2}'.format(d.year, d.month, d.day)
    elif '今月' in text:
        return '{0}/{1}'.format(d.year, d.month)
    elif '来月' in text:
        d = d + timedelta(days=1)
        return '{0}/{1}'.format(d.year, d.month)
    else:
        return False


def judge_my_subjects(l):
    s = []
    for i in l:
        if i.subject in my_subjects:
            s.append(i.subject)
    return s


def return_cancel(status):
    d = datetime.now()
    try:
        date = judge_date(status.text)
        if date is False:
            api.update_status(
                status=' 日付を解析できませんでした．', in_reply_to_status_id=status.id)
        info_list = []
        with Session() as sess:
            query = sess.query(Cancel)
            if len(date) < 8:
                info_list = query.filter(Cancel.day.startswith(date)).all()
            else:
                info_list = query.filter(
                    text('day=:day')).params(day=date).all()
        s = judge_my_subjects(info_list)
        t = ', '.join(s)
        head = '@' + status.user.screen_name
        if 0 < len(t) < 100:
            api.update_status(
                status=head + t, in_reply_to_status_id=status.id_str)
        elif 100 <= len(t):
            a = split_list(s)
            for one in a:
                t = ', '.join(one)
                api.update_status(
                    status=head + t, in_reply_to_status_id=status.id_str)
        else:
            api.update_status(
                status=head +
                ' {0}休講はありません．残念でしたね．'.format(d.strftime("%m/%d %H:%M")),
                in_reply_to_status_id=status.id_str)
    except Exception:
        raise


def return_info(status):
    d = datetime.now()
    try:
        info_list = []
        head = '@' + status.user.screen_name
        m_sub = [s.encode('utf-8') for s in my_subjects]
        with Session() as sess:
            query = sess.query(Info)
            info_list = query.filter(Info.subject.in_(m_sub)).all()
        if len(info_list) is 0:
            api.update_status(
                status=head +
                ' {0}現在受講中の科目に関して，授業関係連絡は掲示されていません．'.format(
                    d.strftime("%m/%d %H:%M")),
                in_reply_to_status_id=status.id_str)
            return False
        s = ""
        for i in info_list:
            s = s + "\n{0}: {1}({2})".format(i.abstract, i.subject, i.id)
        if len(s) > 120:
            for i in info_list:
                s = s + "\n{0}({1})".format(i.subject, i.id)
        api.update_status(status=head + s, in_reply_to_status_id=status.id_str)
    except Exception:
        raise


def return_info_by_id(status):
    try:
        head = '@' + status.user.screen_name
        r = re.compile('(?<=\s)[0-9]+')
        info_num = re.search(r, status.text)
        txt = "授業名: {0}\n教員名: {1}\n概要: {2}\n詳細: {3}\n掲載日: {4}\n更新日: {5}"
        with Session() as sess:
            query = sess.query(Info)
            info = query.filter(Info.id == info_num.group()).first()
            if info is not None:
                txt = txt.format(
                    info.subject, info.teacher, info.abstract,
                    info.detail, info.first, info.up_date)
                api.send_direct_message(user_id=status.user.id, text=txt)
            else:
                api.update_status(status=head + " 存在しないIDです．",
                                  in_reply_to_status_id=status.id_str)
    except Exception:
        raise


def split_list(l):
    a = u""
    i = 0
    while len(a) < 120:
        a = a + u"%s, " % (l[i])
        i += 1
    i -= 1
    s_list = [l[o:o + i] for o in range(0, len(l), i)]
    return s_list


def get_today_cancel(date):
    try:
        d = "{0}/{1}/{2}".format(date.year, date.month, date.day)
        cancels = []
        with Session() as sess:
            query = sess.query(Cancel)
            cancels = query.filter(Cancel.day == d).all()
        cancels = judge_my_subjects(cancels)
        if len(cancels) == 0:
            return "本日休講はありません．"
        else:
            s = ""
            for c in cancels:
                t = "{0}({1})".format(c.subject, c.id)
                s = s + t + "\n"
            return "本日の休講\n" + s
    except Exception:
        raise


def get_today_info():
    try:
        info_list = []
        m_sub = [s.encode('utf-8') for s in my_subjects]
        with Session() as sess:
            query = sess.query(Info)
            info_list = query.filter(Info.subject.in_(m_sub)).all()
        if len(info_list) == 0:
            return "現在掲示中の授業関係連絡はありません．"
        else:
            s = ""
            for c in info_list:
                t = "{0}: {1}({2})".format(c.abstract, c.subject, c.id)
                s = s + t + "\n"
            return s
    except Exception:
        raise
