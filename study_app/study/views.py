from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import StudyTime, Goal, Subject
from accounts.models import CustomUser, Connection
from qa.models import Question, Answer
from qa.forms import SubjectSelectForm
from .forms import StudyTimeForm, GoalCreateForm, SubjectCreateForm
from django.db.models import Q
import datetime as dt
from django_pandas.io import read_frame
from .helpers import to_time_str, get_bar_chart_week, get_bar_chart_month, get_bar_chart_year, get_pie_chart_data


# Create your views here.
class HomeView(LoginRequiredMixin, generic.CreateView):
    template_name = 'home.html'
    form_class = StudyTimeForm
    success_url = reverse_lazy('study:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ログインユーザーがフォローしているユーザーを取得
        following = Connection.objects.filter(follower=self.request.user).values_list('following')
        tab = self.request.GET.get('tab') or 'all'
        if tab == 'all':
            # 自分の記録、フォローユーザーの記録（公開設定がfollow）を取得
            study_times = StudyTime.objects.filter(Q(user=self.request.user)|Q(user__in=following)).exclude(user__in=following, publication='private').order_by('-studied_at').select_related()
        elif tab == 'my-record':
            study_times = StudyTime.objects.filter(user=self.request.user).order_by('-studied_at').select_related()
        elif tab == 'following':
            study_times = StudyTime.objects.filter(user__in=following, publication='follow').order_by('-studied_at').select_related()
        # 時間の表示形式を変更
        for study_time in study_times:
            study_time.minutes = to_time_str(study_time.minutes)

        goals = Goal.objects.filter(user=self.request.user).order_by('-created_at')
        # Queryset型からDataFrame型に変換
        df_goal = read_frame(goals, fieldnames=['pk', 'subject', 'subject__color', 'text', 'date', 'goal_minutes', 'studied_minutes', 'created_at'])
        df_goal['achievement_rate'] = (df_goal['studied_minutes'] * 100 / df_goal['goal_minutes']).astype(int) # 達成率
        today = dt.date.today()
        for i, goal in df_goal.iterrows():
            df_goal.at[i, 'goal_minutes'] = to_time_str(goal['goal_minutes']) # 時間の表示形式を変更
            df_goal.at[i, 'studied_minutes'] = to_time_str(goal['studied_minutes']) # 時間の表示形式を変更
            df_goal.at[i, 'remaining_days'] = (goal['date'] - today).days # 残り日数

        context['tab'] = tab
        context['study_time_list'] = study_times
        context['df_goal'] = df_goal
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

        # 目標の学習時間を更新
        goals = Goal.objects.filter(user=self.request.user, subject=study_time.subject)
        for goal in goals:
            goal.studied_minutes += study_time.minutes
            if (not goal.is_achieved) and (goal.studied_minutes >= goal.goal_minutes):
                goal.is_achieved = True
                messages.info(self.request, '目標を達成しました。')
            goal.save()
        messages.success(self.request, '記録を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '記録の作成に失敗しました。')
        return super().form_invalid(form)


class StudyTimeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = StudyTime
    success_url = reverse_lazy('study:home')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '記録を削除しました。')
        return super().delete(request, *args, **kwargs)


class StudyTimeUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'study_time_update.html'
    model = StudyTime
    fields = ['subject', 'studied_at', 'minutes', 'publication']
    success_url = reverse_lazy('study:home')

    def form_valid(self, form):
        messages.success(self.request, '記録を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "記録の更新に失敗しました。")
        return super().form_invalid(form)


class GoalView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'goal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goals = Goal.objects.filter(user=self.request.user).order_by('-created_at')
        # Queryset型からDataFrame型に変換
        df_goal = read_frame(goals, fieldnames=['pk', 'subject', 'subject__color', 'text', 'date', 'goal_minutes', 'studied_minutes', 'created_at'])
        df_goal['achievement_rate'] = (df_goal['studied_minutes'] * 100 / df_goal['goal_minutes']).astype(int) # 達成率
        today = dt.date.today()
        for i, goal in df_goal.iterrows():
            df_goal.at[i, 'goal_minutes'] = to_time_str(goal['goal_minutes'])
            df_goal.at[i, 'studied_minutes'] = to_time_str(goal['studied_minutes'])
            df_goal.at[i, 'remaining_days'] = (goal['date'] - today).days # 残り日数

        context['df_goal'] = df_goal
        return context


class GoalCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'goal_create.html'
    form_class = GoalCreateForm
    success_url = reverse_lazy('study:home')

    # StudyTimeFormにログインユーザーIDを渡す
    def get_form_kwargs(self):
        kwargs = super(GoalCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        goal = form.save(commit=False)
        # ログインユーザーのIDを保存
        goal.user = self.request.user
        goal.save()

        messages.success(self.request, '目標を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "目標の作成に失敗しました。")
        return super().form_invalid(form)


class GoalUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'goal_update.html'
    model = Goal
    fields = ['subject', 'text', 'date', 'goal_minutes']
    success_url = reverse_lazy('study:goal')

    def form_valid(self, form):
        messages.success(self.request, '目標を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '目標の更新に失敗しました。')
        return super().form_invalid(form)


class ReportView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        study_times = StudyTime.objects.filter(user=self.request.user).order_by('studied_at').select_related()
        # Queryset型からDataFrame型に変換
        df = read_frame(study_times, fieldnames=['subject', 'subject__color', 'studied_at', 'minutes'])
        df2 = df.copy() # コピー(仮)

        # studied_atカラムをdatetime型からdate型に変換
        if not df2.empty:
            df2['studied_at'] = df2['studied_at'].dt.date
        today = dt.date.today()
        context['df'] = df2 # 確認用

        today_sum = df2.query('studied_at == @today').sum()['minutes']

        context['today_sum'] = to_time_str(today_sum) # 今日の合計
        # context['week_sum']
        # context['month_sum']
        # context['total']
        context['bar_chart_week'] = get_bar_chart_week(df.copy(), today)
        context['bar_chart_month'] = get_bar_chart_month(df.copy(), today)
        context['bar_chart_year'] = get_bar_chart_year(df.copy(), today)
        context['pie_chart'] = get_pie_chart_data(df.copy())
        return context


class SubjectView(LoginRequiredMixin, generic.CreateView):
    template_name = 'subject.html'
    form_class = SubjectCreateForm
    success_url = reverse_lazy('study:subject')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_list'] = Subject.objects.filter(user=self.request.user, is_available=True).order_by('created_at')
        return context

    def form_valid(self, form):
        subject = form.save(commit=False)
        # ログインユーザーのIDを保存
        subject.user = self.request.user
        subject.save()

        messages.success(self.request, '教科を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '教科の作成に失敗しました。')
        return super().form_invalid(form)


class SubjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'subject_update.html'
    model = Subject
    fields = ['name', 'color', 'is_learned']
    success_url = reverse_lazy('study:subject')

    def form_valid(self, form):
        messages.success(self.request, '教科を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '教科の更新に失敗しました。')
        return super().form_invalid(form)


@login_required
def subject_delete_view(request, *args, **kwargs):
    subject = Subject.objects.get(pk=kwargs['pk'])
    # 教科を使用不可に設定
    subject.is_available = False
    subject.save()

    messages.success(request, '教科を削除しました。')
    return HttpResponseRedirect(reverse_lazy('study:subject'))


class AccountDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'account_detail.html'
    model = CustomUser
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        account = CustomUser.objects.get(username=username)
        context['account'] = account
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()
        if username is not self.request.user.username:
            result = Connection.objects.filter(follower__username=self.request.user.username).filter(following__username=username)
            context['connected'] = True if result else False
        tab = self.request.GET.get('tab') or 'question'
        if tab == 'question':
            context['question_list'] = Question.objects.filter(user=account)
        elif tab == 'answer':
            context['answer_list'] = Answer.objects.filter(user=account)
        context['tab'] = tab
        context['subject_select_form'] = SubjectSelectForm
        return context


class AccountUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'account_update.html'
    model = CustomUser
    fields = ['icon']
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def form_valid(self, form):
        messages.success(self.request, 'プロフィールを更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'プロフィールの更新に失敗しました。')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('study:account_detail', kwargs={'username': self.request.user.username })

# フォロー
@login_required
def follow_view(request, *args, **kwargs):
    try:
        # フォロワー（ログインユーザー）を取得
        follower = CustomUser.objects.get(username=request.user.username)
        # フォロー対象を取得
        following = CustomUser.objects.get(username=kwargs['username'])
    except CustomUser.DoesNotExist:
        messages.warning(request, f'{kwargs["username"]}は存在しません')
        return HttpResponseRedirect(reverse_lazy('study:home'))
    else:
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
        # フォロワー（ログインユーザー）を取得
        follower = CustomUser.objects.get(username=request.user.username)
        # フォロー解除対象を取得
        following = CustomUser.objects.get(username=kwargs['username'])
        if follower == following:
            messages.warning(request, '自分自身のフォローは外すことができません')
        else:
            unfollow = Connection.objects.get(follower=follower, following=following)
            unfollow.delete()
            messages.success(request, f'あなたは{following.username}のフォローを解除しました')
    except CustomUser.DoesNotExist:
        messages.warning(request, f'{kwargs["username"]}は存在しません')
        return HttpResponseRedirect(reverse_lazy('study:home'))
    except Connection.DoesNotExist:
        messages.warning(request, f'あなたは{following.username}をフォローしませんでした')
        return HttpResponseRedirect(reverse_lazy('study:home'))
    else:
        return HttpResponseRedirect(reverse_lazy('study:account_detail', kwargs={'username': following.username}))
