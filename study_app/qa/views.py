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
        queryset = Question.objects.order_by('-created_at')

        # GETパラメータを取得
        subject = self.request.GET.get('subject')
        status = self.request.GET.get('status')
        query = self.request.GET.get('query')

        if subject:
            queryset = queryset.filter(subject=subject)

        if status == 'answered':
            queryset = queryset.filter(is_answered=True)
        elif status == 'not_answered':
            queryset = queryset.filter(is_answered=False)

        if query:
            queryset = queryset.filter(text__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question_create.html'
    form_class = QuestionCreateForm
    success_url = reverse_lazy('qa:qa')

    def form_valid(self, form):
        question = form.save(commit=False)
        # ログインユーザーのIDを保存
        question.user = self.request.user
        # 締め切りを一週間後に設定
        question.deadline = dt.datetime.now() + dt.timedelta(days=7)
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
