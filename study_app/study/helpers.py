from django.contrib.sessions.models import Session
from .models import CustomUser
import datetime as dt
from dateutil.relativedelta import relativedelta
import calendar


def set_bar_chart_dataset(data, df, start, end):
    date_diff = (end - start).days + 1
    # startからendの期間内のデータを取得
    df = df[(df['studied_at'] >= start) & (df['studied_at'] <= end)]
    # 教科名と教科の色をタプルのリストで取得
    subjects = df.groupby(['subject', 'subject__color']).groups.keys()
    for subject in subjects:
        dataset = {'label': subject[0], 'data': [], 'backgroundColor': subject[1]}
        df2 = df.groupby('subject').get_group(subject[0])
        df2 = df2.groupby('studied_at', as_index=False).sum().reset_index(drop=True)
        for i in range(date_diff):
            for row in df2.itertuples():
                if row.studied_at == (start + dt.timedelta(days=i)):
                    dataset['data'].append(row.study_minutes)
                    break
            else:
                dataset['data'].append(0)
        data['datasets'].append(dataset)
    return data


def get_bar_chart_week(df, today):
    data = {'labels': [], 'datasets': []}
    if not df.empty:
        # studied_atカラムをDatetime型からdate型に変更
        df['studied_at'] = df['studied_at'].dt.date
        weekday = today.isoweekday() % 7
        start = today + dt.timedelta(days=-weekday)
        end = today + dt.timedelta(days=(6-weekday))
        date_diff = (end - start).days + 1
        for i in range(date_diff):
            date = start + dt.timedelta(days=i)
            data['labels'].append(date.strftime('%m/%d') + ' (' + ['日', '月', '火', '水', '木', '金', '土'][date.isoweekday() % 7] + ')')
        data = set_bar_chart_dataset(data, df.copy(), start, end)
    return data


def get_bar_chart_month(df, today):
    data = {'labels': [], 'datasets': []}
    if not df.empty:
        # studied_atカラムをDatetime型からdate型に変更
        df['studied_at'] = df['studied_at'].dt.date
        start = today.replace(day=1)
        end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        date_diff = (end - start).days + 1
        for i in range(date_diff):
            date = start + dt.timedelta(days=i)
            data['labels'].append(date.strftime('%d'))
        data = set_bar_chart_dataset(data, df.copy(), start, end)
    return data

def get_bar_chart_year(df, today):
    data = {'labels': [], 'datasets': []}
    if not df.empty:
        # studied_atカラムをDatetime型からdate型に変更
        df['year'] = df['studied_at'].dt.year
        df['month'] = df['studied_at'].dt.month
        df = df[df['year'] == today.year]
        for i in range(12):
            data['labels'].append(str(i + 1) + '月')
        # 教科名と教科の色をタプルのリストで取得
        subjects = df.groupby(['subject', 'subject__color']).groups.keys()
        for subject in subjects:
            dataset = {'label': subject[0], 'data': [], 'backgroundColor': subject[1]}
            df2 = df.groupby('subject').get_group(subject[0])
            df2 = df2.groupby('month', as_index=False).sum().reset_index(drop=True)
            for i in range(1, 13):
                for row in df2.itertuples():
                    if row.month == i:
                        dataset['data'].append(row.study_minutes)
                        break
                else:
                    dataset['data'].append(0)
            data['datasets'].append(dataset)
    return data

def get_pie_chart_data(df):
    data = {'labels': [], 'datasets': []}
    if not df.empty:
        dataset = {'data': []}
        df = df.groupby(['subject', 'subject__color'], as_index=False).sum().sort_values('study_minutes', ascending=False)
        data['labels'] = df['subject'].values.tolist()
        dataset['data'] = df['study_minutes'].values.tolist()
        dataset['backgroundColor'] = df['subject__color'].values.tolist()
        data['datasets'].append(dataset)
    return data
