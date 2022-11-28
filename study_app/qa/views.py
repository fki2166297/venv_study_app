from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.views import generic
from .models import Question, LikeForQuestion, Answer
from .forms import QuestionCreateForm, AnswerCreateForm, SubjectSelectForm
import datetime as dt


# Create your views here.
class QuestionAndAnswerView(LoginRequiredMixin, generic.ListView):
    template_name = 'qa.html'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('query')
        tab = self.request.GET.get('tab')
        sort = self.request.GET.get('sort')
        subject = self.request.GET.get('subject')

        queryset = Question.objects.order_by('-created_at')
        if query:
            queryset = queryset.filter(text__icontains=query)

        if tab == 'resolved':
            queryset = queryset.filter(is_resolved=True)
        elif tab == 'unresolved':
            queryset = queryset.filter(is_resolved=False)

        if subject:
            queryset = queryset.filter(subject=subject)

        if sort == 'old':
            queryset = queryset.order_by('created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query')
        context['tab'] = self.request.GET.get('tab') or 'all'
        context['sort'] = self.request.GET.get('sort') or 'new'
        context['subject'] = self.request.GET.get('subject')

        context['subject_select_form'] = SubjectSelectForm
        return context


class QuestionDetailView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question_detail.html'
    form_class = AnswerCreateForm

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        context['answer_list'] = Answer.objects.filter(question=self.kwargs['pk'])

        like_for_question = LikeForQuestion.objects.filter(target=self.kwargs['pk'])
        context['like_for_question_count'] = like_for_question.count()
        if like_for_question.filter(user=self.request.user).exists():
            context['is_user_liked_for_question'] = True
        else:
            context['is_user_liked_for_question'] = False
        return context

    def form_valid(self, form):
        answer = form.save(commit=False)
        # ログインユーザーのIDを保存
        answer.user = self.request.user
        # questionのIDを保存
        answer.question = Question.objects.get(pk=self.kwargs['pk'])
        answer.save()

        question = Question.objects.get(pk=self.kwargs['pk'])
        if not question.is_answered:
            question.is_answered = True
            question.save()

        messages.success(self.request, '回答を投稿しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '回答の作成に失敗しました。')
        return super().form_invalid(form)


@login_required
def like_for_question(request):
    context = {
        'user': request.user.username,
    }
    question = get_object_or_404(Question, pk=request.POST.get('question_pk'))
    like = LikeForQuestion.objects.filter(target=question, user=request.user)
    if like.exists():
        like.delete()
        context['method'] = 'delete'
    else:
        like.create(target=question, user=request.user)
        context['method'] = 'create'
    context['like_for_question_count'] = LikeForQuestion.objects.filter(target=question).count()
    return JsonResponse(context)


class SelfResolutionView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'self_resolution.html'
    model = Question
    fields = ['text_self_resolution']

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        question = form.save(commit=False)
        question.is_resolved = True
        question.save()

        messages.success(self.request, '質問を自己解決に設定しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '自己解決の設定に失敗しました。')
        return super().form_invalid(form)


class SetBestAnswerView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'set_best_answer.html'
    model = Question
    fields = ['comment']
    slug_field = 'a_pk'
    slug_url_kwarg = 'a_pk'

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        question = form.save(commit=False)
        question.is_resolved = True
        question.save()

        answer = Answer.objects.get(pk=self.kwargs['a_pk'])
        answer.is_best = True
        answer.save()

        messages.success(self.request, 'ベストアンサーを設定しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ベストアンサーの設定に失敗しました。')
        return super().form_invalid(form)


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question_create.html'
    form_class = QuestionCreateForm
    success_url = reverse_lazy('qa:qa')

    def form_valid(self, form):
        question = form.save(commit=False)
        # ログインユーザーのIDを保存
        question.user = self.request.user
        # 締め切りを一週間後に設定
        deadline = dt.datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=8)
        question.deadline = deadline
        question.save()

        messages.success(self.request, '質問を投稿しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '質問の投稿に失敗しました。')
        return super().form_invalid(form)


class QuestionUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'question_update.html'
    model = Question
    fields = ['supplement']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, '質問を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '質問の更新に失敗しました。')
        return super().form_invalid(form)


@login_required
def question_delete_view(request, *args, **kwargs):
    question = Question.objects.get(pk=kwargs['pk'])
    question.delete()
    messages.success(request, '質問を削除しました。')
    return HttpResponseRedirect(reverse_lazy('qa:qa'))
