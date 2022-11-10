from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import generic
from .models import StudyTime, Subject, Question, Answer
from accounts.models import CustomUser, Connection
from .forms import StudyTimeForm, SubjectCreateForm, QuestionCreateForm, AnswerCreateForm, SubjectSelectForm
from django.db.models import Q
import datetime as dt
import pandas as pd
from django_pandas.io import read_frame
from .helpers import get_current_user, get_bar_chart_week, get_bar_chart_month, get_bar_chart_year

# Create your views here.
class HomeView(LoginRequiredMixin, generic.CreateView):
    template_name = 'home.html'
    form_class = StudyTimeForm
    success_url = reverse_lazy('study:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = 'all'
        # ログインユーザーがフォローしているユーザーのIDをすべて取得
        following = Connection.objects.filter(follower=self.request.user).values_list('following')
        # ログインユーザー、フォローユーザーのデータを取得
        query = StudyTime.objects.filter(Q(user=self.request.user)|Q(user__in=following)).order_by('-studied_at').select_related()
        if 'tab' in self.request.GET:
            # GETパラメータのtabを取得
            tab = self.request.GET['tab']
            if tab == 'my-record':
                query = StudyTime.objects.filter(user=self.request.user).order_by('-studied_at').select_related()
            elif tab == 'following':
                query = StudyTime.objects.filter(user__in=following).order_by('-studied_at').select_related()
        context['tab'] = tab
        context['study_time_list'] = query
        return context

    # StudyTimeFormにログインユーザーIDを渡す
    def get_form_kwargs(self):
        kwargs = super(HomeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        study_time = form.save(commit=False)
        # ログインユーザーのIDを保存
        study_time.user = self.request.user
        study_time.save()
        messages.success(self.request, '記録を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "記録の作成に失敗しました。")
        return super().form_invalid(form)


class ReportView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = StudyTime.objects.filter(user=self.request.user).order_by('studied_at').select_related()
        df = read_frame(query, fieldnames=['subject', 'subject__color', 'studied_at', 'study_minutes'])

        today = dt.date.today()
        context['df'] = df # 確認用
        context['bar_chart_week'] = get_bar_chart_week(df.copy(), today)
        context['bar_chart_month'] = get_bar_chart_month(df.copy(), today)
        context['bar_chart_year'] = get_bar_chart_year(df.copy(), today)
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


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question_create.html'
    form_class = QuestionCreateForm
    success_url = reverse_lazy('study:qa')

    def form_valid(self, form):
        question = form.save(commit=False)
        # ログインユーザーのIDを保存
        question.user = self.request.user
        question.save()
        return super().form_valid(form)


class QuestionDetailView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question_detail.html'
    form_class = AnswerCreateForm

    def get_success_url(self):
        return reverse_lazy('study:question_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        context['answer_list'] = Answer.objects.filter(question=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        answer = form.save(commit=False)
        # ログインユーザーのIDを保存
        answer.user = self.request.user
        # questionのIDを保存
        answer.question = Question.objects.get(pk=self.kwargs['pk'])
        answer.save()
        return super().form_valid(form)


class SubjectView(LoginRequiredMixin, generic.CreateView):
    template_name = 'subject.html'
    form_class = SubjectCreateForm
    success_url = reverse_lazy('study:subject')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_list'] = Subject.objects.filter(user=self.request.user).order_by('created_at')
        return context

    def form_valid(self, form):
        subject = form.save(commit=False)
        # ログインユーザーのIDを保存
        subject.user = self.request.user
        subject.save()
        return super().form_valid(form)

# フォロー
@login_required
def follow_view(request, *args, **kwargs):
    try:
        follower = CustomUser.objects.get(username=request.user.username)
        following = CustomUser.objects.get(username=kwargs['username'])
    except CustomUser.DoesNotExist:
        messages.warning(request, f'{kwargs["username"]}は存在しません')
        return HttpResponseRedirect(reverse_lazy('study:home'))
    if follower == following:
        messages.warning(request, '自分自身はフォローできません')
    else:
        _, created = Connection.objects.get_or_create(follower=follower, following=following)
        if (created):
            messages.success(request, f'{following.username}をフォローしました')
        else:
            messages.warning(request, f'あなたはすでに{following.username}をフォローしています')

    return HttpResponseRedirect(reverse_lazy('study:account_detail', kwargs={'username': following.username}))

# フォロー解除
@login_required
def unfollow_view(request, *args, **kwargs):
    try:
        follower = CustomUser.objects.get(username=request.user.username)
        following = CustomUser.objects.get(username=kwargs['username'])
        if follower == following:
            messages.warning(request, '自分自身のフォローを外せません')
        else:
            unfollow = Connection.objects.get(follower=follower, following=following)
            unfollow.delete()
            messages.success(request, f'あなたは{following.username}のフォローを解除しました')
    except CustomUser.DoesNotExist:
        messages.warning(request, f'{kwargs["username"]}は存在しません')
        return HttpResponseRedirect(reverse_lazy('study:home'))
    except Connection.DoesNotExist:
        messages.warning(request, f'あなたは{following.username}をフォローしませんでした')

    return HttpResponseRedirect(reverse_lazy('study:account_detail', kwargs={'username': following.username}))

# プロフィール画面
class AccountDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'account_detail.html'
    model = CustomUser
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        context['username'] = username
        context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()

        if username is not context['user'].username:
            result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
            context['connected'] = True if result else False

        return context
