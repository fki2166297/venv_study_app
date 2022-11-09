from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import generic
from .models import StudyTime, Subject, Question, Answer
from accounts.models import CustomUser, Connection
from accounts.forms import CustomUserForm
from .forms import StudyTimeForm, SubjectCreateForm, QuestionCreateForm, AnswerCreateForm, SubjectSelectForm
from django.db.models import Q
import datetime as dt
import calendar
import pandas as pd
from django_pandas.io import read_frame
from .helpers import get_current_user, get_bar_chart_week

# Create your views here.
class HomeView(LoginRequiredMixin, generic.CreateView):
    template_name = 'home.html'
    model = StudyTime
    form_class = StudyTimeForm
    success_url = reverse_lazy('study:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = 'all'
        # ログインユーザーがフォローしているユーザーのIDをすべて取得
        following = Connection.objects.filter(follower=self.request.user).values_list('following')
        query = self.model.objects.filter(Q(user=self.request.user)|Q(user__in=following)).order_by('-studied_at').select_related()
        if 'tab' in self.request.GET:
            tab = self.request.GET['tab']
            if tab == 'my-record':
                query = self.model.objects.filter(user=self.request.user).order_by('-studied_at').select_related()
            elif tab == 'following':
                query = self.model.objects.filter(user__in=following).order_by('-studied_at').select_related()
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
        study_time.user = self.request.user
        study_time.save()
        messages.success(self.request, '記録を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "記録の作成に失敗しました。")
        return super().form_invalid(form)


class StudyTimeUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'study_time_update.html'
    model = StudyTime
    success_url = reverse_lazy('study:home')


class StudyTimeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = StudyTime
    success_url = reverse_lazy('study:home')


class ReportView(LoginRequiredMixin, generic.TemplateView):
    model = StudyTime
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.model.objects.filter(user=self.request.user).order_by('studied_at').select_related()
        df = read_frame(query, fieldnames=['subject', 'subject__color', 'studied_at', 'study_minutes'])

        # studied_atカラムをdatetime型からdate型に変換
        if not df.empty:
            df['studied_at'] = df['studied_at'].dt.date

        today = dt.date.today()
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

        context['df'] = df2
        context['data'] = get_bar_chart_week(df)
        context['subject'] = subjects

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
        answer.user = self.request.user
        # questionのIDを保存
        answer.question = Question.objects.get(pk=self.kwargs['pk'])
        answer.save()
        return super().form_valid(form)


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question_create.html'
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

# フォロー
@login_required
def follow_view(request, *args, **kwargs):
    try:
        # request.user.username = ログインユーザーのユーザー名を渡す。
        follower = CustomUser.objects.get(username=request.user.username)
        #kwargs['username'] = フォロー対象のユーザー名を渡す。
        following = CustomUser.objects.get(username=kwargs['username'])
    # フォロー対象が存在しない場合
    except CustomUser.DoesNotExist:
        messages.warning(request, f'{kwargs["username"]}は存在しません')
        return HttpResponseRedirect(reverse_lazy('study:home'))
    # フォローしようとしている対象が自分の場合
    if follower == following:
        messages.warning(request, '自分自身はフォローできません')
    else:
        # フォロー対象をまだフォローしていなければ、DBにフォロワー(自分)×フォロー(相手)という組み合わせで登録する。
        # createdにはTrueが入る
        _, created = Connection.objects.get_or_create(follower=follower, following=following)

        # もしcreatedがTrueの場合、フォロー完了のメッセージを表示させる。
        if (created):
            messages.success(request, f'{following.username}をフォローしました')
        # 既にフォロー相手をフォローしていた場合、createdにはFalseが入る。
        # フォロー済みのメッセージを表示させる。
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
            # フォロワー(自分)×フォロー(相手)という組み合わせを削除する。
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
    model = CustomUser
    template_name = 'account_detail.html'

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
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
