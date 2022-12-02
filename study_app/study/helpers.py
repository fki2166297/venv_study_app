from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime as dt
import calendar


def to_time_str(minutes):
    if minutes == 0:
        return '0分'
    h, m = divmod(minutes, 60)
    return (str(h) + '時間' if h else '') + (str(m) + '分' if m else '')

def get_bar_chart_week(df, today):
    data = {'labels': [], 'datasets': []}
    if not df.empty:
        weekday = today.isoweekday() % 7
        start = today + dt.timedelta(days=-weekday)
        end = today + dt.timedelta(days=(6 - weekday))

        # studied_atカラムをDatetime型からdate型に変更
        df['studied_at'] = df['studied_at'].dt.date
        # x軸ラベルの設定
        for i in range(7):
            date = start + dt.timedelta(days=i)
            data['labels'].append(date.strftime('%m/%d') + ' (' + ['日', '月', '火', '水', '木', '金', '土'][date.isoweekday() % 7] + ')')
        # startからendの期間内のデータを取得
        df = df.query('@start <= studied_at <= @end')
        # 教科名と教科の色をタプルのリストで取得
        subjects = df.groupby(['subject', 'subject__color']).groups.keys()
        for subject in subjects:
            dataset = {'label': subject[0], 'data': [], 'backgroundColor': subject[1]}
            df2 = df.groupby('subject').get_group(subject[0])
            df2 = df2.groupby('studied_at', as_index=False).sum().reset_index(drop=True)
            for i in range(7):
                for row in df2.itertuples():
                    if row.studied_at == (start + dt.timedelta(days=i)):
                        dataset['data'].append(row.minutes)
                        break
                else:
                    dataset['data'].append(0)
            data['datasets'].append(dataset)
    return data

def get_bar_chart_month(df, today):
    data = {'labels': [], 'datasets': []}
    if not df.empty:
        DAYS = calendar.monthrange(today.year, today.month)[1]
        start = today.replace(day=1)

        df['month'] = df['studied_at'].dt.month
        for i in range(DAYS):
            data['labels'].append(i + 1)
        df = df.query('month == @today.month')
        # 教科名と教科の色をタプルのリストで取得
        subjects = df.groupby(['subject', 'subject__color']).groups.keys()
        for subject in subjects:
            dataset = {'label': subject[0], 'data': [], 'backgroundColor': subject[1]}
            df2 = df.groupby('subject').get_group(subject[0])
            df2 = df2.groupby('studied_at', as_index=False).sum().reset_index(drop=True)
            for i in range(DAYS):
                for row in df2.itertuples():
                    if row.studied_at == (start + dt.timedelta(days=i)):
                        dataset['data'].append(row.minutes)
                        break
                else:
                    dataset['data'].append(0)
            data['datasets'].append(dataset)
    return data

def get_bar_chart_year(df, today):
    data = {'labels': [], 'datasets': []}
    if not df.empty:
        df['year'] = df['studied_at'].dt.year
        df['month'] = df['studied_at'].dt.month
        for i in range(12):
            data['labels'].append(str(i + 1) + '月')
        df = df.query('year == @today.year')
        # 教科名と教科の色をタプルのリストで取得
        subjects = df.groupby(['subject', 'subject__color']).groups.keys()
        for subject in subjects:
            dataset = {'label': subject[0], 'data': [], 'backgroundColor': subject[1]}
            df2 = df.groupby('subject').get_group(subject[0])
            df2 = df2.groupby('month', as_index=False).sum().reset_index(drop=True)
            for i in range(1, 13):
                for row in df2.itertuples():
                    if row.month == i:
                        dataset['data'].append(row.minutes)
                        break
                else:
                    dataset['data'].append(0)
            data['datasets'].append(dataset)
    return data

def get_pie_chart_data(df):
    data = {'labels': [], 'datasets': []}
    if not df.empty:
        dataset = {'data': []}
        df = df.groupby(['subject', 'subject__color'], as_index=False).sum().sort_values('minutes', ascending=False)
        data['labels'] = df['subject'].values.tolist()
        dataset['data'] = df['minutes'].values.tolist()
        dataset['backgroundColor'] = df['subject__color'].values.tolist()
        data['datasets'].append(dataset)
    return data

def get_today_sum(df, today):
    if df.empty:
        return 0
    else:
        df['studied_at'] = df['studied_at'].dt.date
        return df.query('studied_at == @today')['minutes'].sum()

def get_week_sum(df, today):
    if df.empty:
        return 0
    else:
        df['studied_at'] = df['studied_at'].dt.date
        weekday = today.isoweekday() % 7
        week_start = today + dt.timedelta(days=-weekday)
        week_end = today + dt.timedelta(days=(6 - weekday))
        return df.query('@week_start <= studied_at <= @week_end')['minutes'].sum()

def get_month_sum(df, today):
    if df.empty:
        return 0
    else:
        df['month'] = df['studied_at'].dt.month
        df['year'] = df['studied_at'].dt.year
        df['studied_at'] = df['studied_at'].dt.date
        return df.query('month == @today.month')['minutes'].sum()

def get_total(df, today):
    if df.empty:
        return 0
    else:
        return df['minutes'].sum()
