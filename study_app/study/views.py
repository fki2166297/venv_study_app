from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView
from .models import StudyTime, Subject, Question, Answer
from .forms import StudyTimeForm, SubjectCreateForm, QuestionCreateForm, AnswerCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime as dt
import pandas as pd
from django_pandas.io import read_frame

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'


class HomeView(LoginRequiredMixin, CreateView):
    template_name = 'home.html'
    model = StudyTime
    form_class = StudyTimeForm
    success_url = reverse_lazy('study:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        COLS = ['subject', 'start_date', 'start_time', 'end_date', 'end_time']
        df = read_frame(self.model.objects.filter(user=self.request.user).select_related(), fieldnames=COLS)

        for index, row in df.iterrows():
            start_dt = dt.datetime.combine(row['start_date'], row['start_time'])
            end_dt = dt.datetime.combine(row['end_date'], row['end_time'])
            df.at[index, 'start'] = start_dt
            df.at[index, 'end'] = end_dt
            dt_diff = end_dt - start_dt
            study_minutes = int(dt_diff.days * 60 * 24 + dt_diff.seconds / 60)
            if study_minutes < 60:
                df.at[index, 'study_time'] = str(study_minutes) + '分'
            else:
                study_hours, study_minutes = divmod(study_minutes, 60)
                if study_minutes == 0:
                    df.at[index, 'study_time'] = str(study_hours) + '時間'
                else:
                    df.at[index, 'study_time'] = str(study_hours) + '時間' + str(study_minutes) + '分'
        df = df.drop(columns=['start_date', 'start_time', 'end_date', 'end_time'])
        context['df_context'] = df
        context['test'] = self.model.objects.filter(user=self.request.user).select_related()
        return context

    # forms.pyにログインユーザーIDを渡す
    def get_form_kwargs(self):
        kwargs = super(HomeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        study_time = form.save(commit=False)
        study_time.user = self.request.user
        study_time.save()
        return super().form_valid(form)


class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'report.html'
    model = StudyTime

    # 棒グラフのデータを取得
    def get_bar_chart_data(self, df, start, end):
        data = {'labels': [], 'datasets': []}
        date_diff = (end - start).days + 1
        # startからendまでの日付をlabelsに格納
        for i in range(date_diff):
            data['labels'].append((start + dt.timedelta(days=i)).strftime('%m/%d'))
        # startからendの期間内のデータを取得
        df = df[(df['date'] >= start) & (df['date'] <= end)]
        # 教科, 日付ごとに学習時間を合計
        df = df.groupby(['subject', 'date'], as_index=False).sum().sort_values(['subject', 'date'])
        subjects = list(df.groupby('subject').groups.keys())
        for subject in subjects:
            dataset = {'label': subject, 'data': [], 'stack': 'stack-1'}
            for i in range(date_diff):
                for row in df.itertuples():
                    if (subject == row.subject) and (start + dt.timedelta(days=i) == row.date):
                        dataset['data'].append(row.study_minutes)
                        break
                else:
                    dataset['data'].append(0)
            data['datasets'].append(dataset)
        return data

    # 円グラフのデータを取得
    def get_pie_chart_data(self, df):
        data = {'labels': [], 'datasets': []}

        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        COLS = ['subject', 'start_date', 'start_time', 'end_date', 'end_time']
        df = read_frame(self.model.objects.filter(user=self.request.user), fieldnames=COLS)

        # 複数の日をまたぐデータを日付ごとに分割する
        df2 = df[(df['start_date']) == (df['end_date'])]
        df3 = df[(df['start_date']) < (df['end_date'])]
        for row in df3.itertuples():
            date_diff = row.end_date - row.start_date
            for i in range(date_diff.days + 1):
                if i == 0:
                    df4 = pd.DataFrame(
                        [[row.subject, row.start_date, row.start_time, row.start_date + dt.timedelta(days=(i+1)), dt.time(00, 00, 00)]],
                        columns=COLS
                    )
                elif i == (date_diff.days):
                    df4 = pd.DataFrame(
                        [[row.subject, row.end_date, dt.time(00, 00, 00), row.end_date, row.end_time]],
                        columns=COLS
                    )
                else:
                    df4 = pd.DataFrame(
                        [[row.subject, row.start_date + dt.timedelta(days=i), dt.time(00, 00, 00), row.start_date + dt.timedelta(days=(i+1)), dt.time(00, 00, 00)]],
                        columns=COLS
                    )
                df2 = pd.concat([df2, df4], axis=0, ignore_index=True)
        for index, row in df2.iterrows():
            start_dt = dt.datetime.combine(row['start_date'], row['start_time'])
            end_dt = dt.datetime.combine(row['end_date'], row['end_time'])
            dt_diff = end_dt - start_dt
            df2.at[index, 'study_minutes'] = dt_diff.days * 60 * 24 + dt_diff.seconds / 60
        df2 = df2.sort_values(['start_date', 'start_time'], ignore_index=True)
        df2 = df2.drop(columns=['start_time', 'end_date', 'end_time'])
        df2 = df2.rename(columns={'start_date': 'date'})

        today = dt.date.today()
        weekday = today.isoweekday() % 7
        week_start = today + dt.timedelta(days=-weekday)
        week_end = today + dt.timedelta(days=(6-weekday))

        context['bar_chart_week'] = self.get_bar_chart_data(df2, week_start, week_end)
        return context


class QuestionAndAnswerView(LoginRequiredMixin, ListView):
    template_name = 'qa.html'

    def get_queryset(self):
        queryset = Question.objects.filter(user=self.request.user).order_by('-created_at')
        return queryset


class QuestionDetailView(LoginRequiredMixin, CreateView):
    template_name = 'question-detail.html'
    model = Question
    form_class = AnswerCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_detail'] = self.model.objects.filter(id=self.kwargs['pk'])[0]
        return context


class QuestionCreateView(LoginRequiredMixin, CreateView):
    template_name = 'question-create.html'
    model = Question
    form_class = QuestionCreateForm
    success_url = reverse_lazy('study:qa')

    def form_valid(self, form):
        question = form.save(commit=False)
        question.user = self.request.user
        question.save()
        return super().form_valid(form)


class SubjectView(LoginRequiredMixin, CreateView):
    template_name = 'subject.html'
    model = Subject
    form_class = SubjectCreateForm
    success_url = reverse_lazy('study:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_list'] = self.model.objects.filter(user=self.request.user).order_by('created_at')
        return context

    def form_valid(self, form):
        subject = form.save(commit=False)
        subject.user = self.request.user
        subject.save()
        return super().form_valid(form)


class MyPageView(LoginRequiredMixin, TemplateView):
    template_name = 'my-page.html'
