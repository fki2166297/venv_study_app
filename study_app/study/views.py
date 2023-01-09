from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import StudyTime, Subject
from accounts.models import CustomUser, Connection
from qa.models import Question, Answer
from qa.forms import SubjectSelectForm
from .forms import StudyTimeForm, SubjectCreateForm
from django.db.models import Q
import datetime as dt
from django_pandas.io import read_frame
from .helpers import to_time_str, get_bar_chart_week, get_bar_chart_month, get_bar_chart_year, get_pie_chart_data, get_today_sum, get_week_sum, get_month_sum, get_total


# Create your views here.
class HomeView(LoginRequiredMixin, generic.ListView):
    template_name = 'home.html'
    paginate_by = 30

    def get_queryset(self):
        # ログインユーザーがフォローしているユーザーを取得
        following = Connection.objects.filter(follower=self.request.user).values_list('following')
        # 自分の記録、フォローユーザーの記録（公開設定がfollow）を取得
        queryset = StudyTime.objects.filter(Q(user=self.request.user)|Q(user__in=following)).exclude(user__in=following, publication='private').order_by('-studied_at').select_related()
        tab = self.request.GET.get('tab')
        if tab == 'my-record':
            queryset = queryset.filter(user=self.request.user).order_by('-studied_at').select_related()
        elif tab == 'following':
            queryset = StudyTime.objects.filter(user__in=following, publication='follow').order_by('-studied_at').select_related()
        # 時間の表示形式を変更
        for studytime in queryset:
            studytime.minutes = to_time_str(studytime.minutes)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab') or 'all'
        context['tab'] = tab
        return context


class StudyTimeCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'studytime_create.html'
    form_class = StudyTimeForm
    success_url = reverse_lazy('study:home')

    # StudyTimeFormにログインユーザーIDを渡す
    def get_form_kwargs(self):
        kwargs = super(StudyTimeCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        studytime = form.save(commit=False)
        # ログインユーザーのIDを保存
        studytime.user = self.request.user
        studytime.save()

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
    template_name = 'studytime_update.html'
    model = StudyTime
    fields = ['subject', 'studied_at', 'minutes', 'publication']
    success_url = reverse_lazy('study:home')

    def form_valid(self, form):
        messages.success(self.request, '記録を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "記録の更新に失敗しました。")
        return super().form_invalid(form)


class ReportView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        studytimes = StudyTime.objects.filter(user=self.request.user).order_by('studied_at').select_related()
        # Queryset型からDataFrame型に変換
        df = read_frame(studytimes, fieldnames=['subject', 'subject__color', 'studied_at', 'minutes'])

        today = dt.date.today()

        context['bar_chart_week'] = get_bar_chart_week(df.copy(), today)
        context['bar_chart_month'] = get_bar_chart_month(df.copy(), today)
        context['bar_chart_year'] = get_bar_chart_year(df.copy(), today)
        context['pie_chart'] = get_pie_chart_data(df.copy())

        context['today_sum'] = to_time_str(get_today_sum(df.copy(), today))
        context['week_sum'] = to_time_str(get_week_sum(df.copy(), today))
        context['month_sum'] = to_time_str(get_month_sum(df.copy(), today))
        context['total'] = to_time_str(get_total(df.copy(), today))
        return context


class SubjectView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'subject.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_list'] = Subject.objects.filter(user=self.request.user, is_available=True).order_by('created_at')
        return context


class SubjectCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'subject_create.html'
    form_class = SubjectCreateForm

    def get_success_url(self):
        via = self.request.GET.get('via')
        if via == 'studytime-create':
            return reverse_lazy('study:studytime_create')
        return reverse_lazy('study:subject')

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
    fields = ['name', 'color']
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


class AccountSearchView(LoginRequiredMixin, generic.ListView):
    template_name = 'accout_search.html'

    def get_queryset(self):
        queryset = CustomUser.objects.none()
        query = self.request.GET.get('query')
        if query:
            queryset = CustomUser.objects.filter(username__icontains=query)
        return queryset


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

        studytimes = StudyTime.objects.filter(user=self.request.user).order_by('studied_at').select_related()
        # Queryset型からDataFrame型に変換
        df = read_frame(studytimes, fieldnames=['subject', 'subject__color', 'studied_at', 'minutes'])

        today = dt.date.today()

        context['today_sum'] = to_time_str(get_today_sum(df.copy(), today))
        context['week_sum'] = to_time_str(get_week_sum(df.copy(), today))
        context['month_sum'] = to_time_str(get_month_sum(df.copy(), today))
        context['total'] = to_time_str(get_total(df.copy(), today))

        context['question_list'] = Question.objects.filter(user=account)
        context['answer_list'] = Answer.objects.filter(user=account)

        context['subject_select_form'] = SubjectSelectForm
        return context


class AccountUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'account_update.html'
    model = CustomUser
    fields = ['username', 'icon']
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def form_valid(self, form):
        account = form.save(commit=False)
        self.request.user.username = account.username

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


@login_required
def check_username_exists(request, *args, **kwargs):
    username = request.POST.get('username')
    username_old = request.user.username
    context = {
        'username': username,
    }
    print(username)
    if CustomUser.objects.filter(username=username).exclude(username=username_old).exists():
        context['is_exist'] = 'true'
    else:
        context['is_exist'] = 'false'
    return JsonResponse(context)
