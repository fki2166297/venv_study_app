from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from .models import StudyTime, Subject, Question, Answer
from accounts.models import CustomUser
from accounts.forms import CustomUserForm
from .forms import StudyTimeForm, SubjectCreateForm, QuestionCreateForm, AnswerCreateForm, SubjectSelectForm
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime as dt
import calendar
import pandas as pd
from django_pandas.io import read_frame

# Create your views here.
class IndexView(generic.TemplateView):
    template_name = 'index.html'


class HomeView(LoginRequiredMixin, generic.CreateView):
    template_name = 'home.html'
    model = StudyTime
    form_class = StudyTimeForm
    success_url = reverse_lazy('study:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study_time_list'] = self.model.objects.filter(user=self.request.user).order_by('-studied_at')
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


class StudyTimeUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'study-time-update.html'
    model = StudyTime
    success_url = reverse_lazy('study:home')


class StudyTimeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = StudyTime
    success_url = reverse_lazy('study:home')


class ReportView(LoginRequiredMixin, generic.TemplateView):
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
            df = df[(df['studied_at'] >= start) & (df['studied_at'] <= end)]
            # 教科, 日付ごとに学習時間を合計
            df = df.groupby(['subject', 'subject__color', 'studied_at'], as_index=False).sum().sort_values(['subject', 'studied_at'])
            subjects = list(df.groupby('subject').groups.keys())
            for subject in subjects:
                dataset = {'label': subject, 'data': [], 'backgroundColor': '', 'stack': 'stack-1'}
                for i in range(date_diff):
                    for row in df.itertuples():
                        if (subject == row.subject) and (start + dt.timedelta(days=i) == row.studied_at):
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
        cols = ['subject', 'subject__color', 'studied_at', 'study_minutes']
        df = read_frame(self.model.objects.filter(user=self.request.user).order_by('-studied_at'), fieldnames=cols)
        # studied_atカラムをdatetime型からdate型に変換
        df['studied_at'] = df['studied_at'].dt.date

        context['df2'] = df

        today = dt.date.today()
        weekday = today.isoweekday() % 7
        week_start = today + dt.timedelta(days=-weekday)
        week_end = today + dt.timedelta(days=(6-weekday))

        month_start = today.replace(day=1)
        month_end = today.replace(day=calendar.monthrange(today.year, today.month)[1])

        context['bar_chart_week'] = self.get_bar_chart_data(df, week_start, week_end)
        context['bar_chart_month'] = self.get_bar_chart_data(df, month_start, month_end)
        context['pie_chart'] = self.get_pie_chart_data(df)
        return context


class QuestionAndAnswerView(LoginRequiredMixin, generic.ListView):
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


class QuestionDetailView(LoginRequiredMixin, generic.CreateView):
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


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question-create.html'
    model = Question
    form_class = QuestionCreateForm
    success_url = reverse_lazy('study:qa')

    def form_valid(self, form):
        question = form.save(commit=False)
        question.user = self.request.user
        question.save()
        return super().form_valid(form)


class SubjectView(LoginRequiredMixin, generic.CreateView):
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


class MyPageView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'my-page.html'
    model = CustomUser
    form_class = CustomUserForm
    success_url = reverse_lazy('study:my-page')

    def get_success_url(self):
        return reverse_lazy('study:my-page', kwargs={'pk': self.kwargs['pk']})

    # def form_valid(self, form):
    #     account = form.save(commit=False)
    #     account.save()
    #     return super().form_valid(form)
