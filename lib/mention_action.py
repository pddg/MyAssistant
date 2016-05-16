from datetime import datetime, timedelta
from sqlalchemy import text
from lib.session import Session
from lib.models import Cancel, Info
from lib.settings import my_subjects
from lib.stream import api


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
    try:
        date = judge_date(status.text)
        if date is False:
            api.update_status(
                status='日付を解析できませんでした．', in_reply_to_status_id=status.id)
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
                status=head + ' 休講はありません．残念でしたね．', in_reply_to_status_id=status.id_str)
    except Exception:
        raise


def return_info(status):
    try:
        info_list = []
        head = '@' + status.user.screen_name
        m_sub = [s.encode('utf-8') for s in my_subjects]
        with Session() as sess:
            query = sess.query(Info)
            info_list = query.filter(Info.subject.in_(m_sub)).all()
        if len(info_list) is 0:
            api.update_status(
                status=head + '現在受講中の科目に関して，授業関係連絡は掲示されていません．', in_reply_to_status_id=status.id_str)
            return False
        s = ""
        for i in info_list:
            s = s + "\n{0}: {1}({2})".format(i.abstract, i.subject, i.id)
        if len(s) > 120:
            for i in info_list:
                s = s + "\n{1}({2})".format(i.subject, i.id)
        api.update_status(status=head + s, in_reply_to_status_id=status.id_str)
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
