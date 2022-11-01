from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView
from .models import StudyTime, Subject, Question, Answer
from accounts.models import CustomUser
from .forms import StudyTimeForm, SubjectCreateForm, QuestionCreateForm, AnswerCreateForm, SubjectSelectForm
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime as dt
import calendar
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
        COLS = ['id', 'subject', 'subject__color', 'start_date', 'start_time', 'end_date', 'end_time', 'study_minutes', 'created_at', 'updated_at']
        df = read_frame(self.model.objects.filter(user=self.request.user), fieldnames=COLS)
        for index, row in df.iterrows():
            if row.study_minutes < 60:
                df.at[index, 'study_minutes'] = str(row.study_minutes) + '分'
            else:
                study_hours, study_minutes = divmod(row.study_minutes, 60)
                if study_minutes == 0:
                    df.at[index, 'study_minutes'] = str(study_hours) + '時間'
                else:
                    df.at[index, 'study_minutes'] = str(study_hours) + '時間' + str(study_minutes) + '分'
        df = df.rename(columns={'study_minutes': 'study_time'})
        context['df_study_time'] = df
        return context

    # forms.pyにログインユーザーIDを渡す
    def get_form_kwargs(self):
        kwargs = super(HomeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        study_time = form.save(commit=False)
        study_time.user = self.request.user
        start_dt = dt.datetime.combine(study_time.start_date, study_time.start_time)
        end_dt = dt.datetime.combine(study_time.end_date, study_time.end_time)
        dt_diff = end_dt - start_dt
        study_time.study_minutes = int(dt_diff.days * 60 * 24 + dt_diff.seconds / 60)
        study_time.save()
        return super().form_valid(form)


class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'report.html'
    model = StudyTime

    # 棒グラフのデータを取得
    def get_bar_chart_data(self, df, start, end):
        data = {'labels': [], 'datasets': []}
        if not df.empty:
            date_diff = (end - start).days + 1
            # startからendまでの日付をlabelsに格納
            for i in range(date_diff):
                data['labels'].append((start + dt.timedelta(days=i)).strftime('%m/%d'))
            # startからendの期間内のデータを取得
            df = df[(df['date'] >= start) & (df['date'] <= end)]
            # 教科, 日付ごとに学習時間を合計
            df = df.groupby(['subject', 'subject__color', 'date'], as_index=False).sum().sort_values(['subject', 'date'])
            subjects = list(df.groupby('subject').groups.keys())
            for subject in subjects:
                dataset = {'label': subject, 'data': [], 'backgroundColor': '', 'stack': 'stack-1'}
                for i in range(date_diff):
                    for row in df.itertuples():
                        if (subject == row.subject) and (start + dt.timedelta(days=i) == row.date):
                            dataset['data'].append(row.study_minutes)
                            dataset['backgroundColor'] = row.subject__color # 仮
                            break
                    else:
                        dataset['data'].append(0)
                data['datasets'].append(dataset)
        return data

    # 円グラフのデータを取得
    def get_pie_chart_data(self, df):
        data = {'labels': [], 'datasets': []}
        dataset = {'data': []}
        if not df.empty:
            df = df.groupby(['subject', 'subject__color'], as_index=False).sum().sort_values('study_minutes', ascending=False)
            data['labels'] = df['subject'].values.tolist()
            dataset['data'] = df['study_minutes'].values.tolist()
            dataset['backgroundColor'] = df['subject__color'].values.tolist()
            data['datasets'].append(dataset)
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cols = ['subject', 'subject__color', 'start_date', 'start_time', 'end_date', 'end_time', 'study_minutes']
        df = read_frame(self.model.objects.filter(user=self.request.user), fieldnames=cols)

        # 複数の日をまたぐデータを日付ごとに分割する
        cols = ['subject', 'subject__color', 'date', 'study_minutes']
        df2 = pd.DataFrame(columns=cols)
        for row in df.itertuples():
            if row.start_date == row.end_date:
                df3 = pd.DataFrame([[row.subject, row.subject__color, row.start_date, row.study_minutes]], columns=cols)
                df2 = pd.concat([df2, df3], axis=0, ignore_index=True)
            else:
                date_diff = row.end_date - row.start_date
                for i in range(date_diff.days + 1):
                    if i == 0:
                        date = row.start_date
                        study_minutes = 60 * 24 - (row.start_time.hour * 60 + row.start_time.minute)
                    elif i < (date_diff.days):
                        date = row.start_date + dt.timedelta(days=i)
                        study_minutes = 60 * 24
                    else:
                        date = row.end_date
                        study_minutes = row.end_time.hour * 60 + row.end_time.minute
                    df3 = pd.DataFrame([[row.subject, row.subject__color, date, study_minutes]], columns=cols)
                    df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        context['df2'] = df2

        today = dt.date.today()
        weekday = today.isoweekday() % 7
        week_start = today + dt.timedelta(days=-weekday)
        week_end = today + dt.timedelta(days=(6-weekday))

        month_start = today.replace(day=1)
        month_end = today.replace(day=calendar.monthrange(today.year, today.month)[1])

        context['bar_chart_week'] = self.get_bar_chart_data(df2, week_start, week_end)
        context['bar_chart_month'] = self.get_bar_chart_data(df2, month_start, month_end)
        context['pie_chart'] = self.get_pie_chart_data(df2)
        return context


class QuestionAndAnswerView(LoginRequiredMixin, ListView):
    template_name = 'qa.html'
    paginate_by = 10

    def get_queryset(self):
        subject = self.request.GET.get('subject')
        if subject:
            queryset = Question.objects.filter(subject=subject).order_by('-created_at')
        else:
            queryset = Question.objects.order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_select_form'] = SubjectSelectForm
        return context


class QuestionDetailView(LoginRequiredMixin, CreateView):
    template_name = 'question-detail.html'
    form_class = AnswerCreateForm

    def get_success_url(self):
        return reverse_lazy('study:question-detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        context['answer_list'] = Answer.objects.filter(question=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.user = self.request.user
        # questionのIDを保存
        answer.question = Question.objects.get(pk=self.kwargs['pk'])
        answer.save()
        return super().form_valid(form)


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
    success_url = reverse_lazy('study:subject')

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
