from django.contrib.sessions.models import Session
from .models import CustomUser

def get_current_user(request=None):
    if not request:
        return None

    session_key = request.session.session_key
    session = Session.objects.get(session_key=session_key).get_decoded()
    uid = session.get('_auth_user_id')

    return CustomUser.objects.get(id=uid)

def get_bar_chart_week(df, today):
    weekday = today.isoweekday() % 7
    start = today + dt.timedelta(days=-weekday)
    end = today + dt.timedelta(days=(6-weekday))

    # 棒グラフのデータ
    data = {'labels': [], 'datasets': []}

    for i in range(7):
        date = start + dt.timedelta(days=i)
        data['labels'].append(date.strftime('%m/%d') + ' (' + ['日', '月', '火', '水', '木', '金', '土'][date.isoweekday() % 7] + ')')

    # startからendの期間内のデータを取得
    df = df[(df['studied_at'] >= start) & (df['studied_at'] <= end)]

    # 教科名と教科の色をタプルのリストで取得
    subjects = df.groupby(['subject', 'subject__color']).groups.keys()

    for subject in subjects:
        dataset = {'label': subject[0], 'data': [], 'backgroundColor': subject[1]}
        df2 = df.groupby('subject').get_group(subject[0])
        df2 = df2.groupby('studied_at', as_index=False).sum().reset_index(drop=True)
        for i in range(7):
            for row in df2.itertuples():
                if row.studied_at == (start + dt.timedelta(days=i)):
                    dataset['data'].append(row.study_minutes)
                    break
            else:
                dataset['data'].append(0)
        data['datasets'].append(dataset)

    return data