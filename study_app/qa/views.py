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
    paginate_by = 30

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


class QuestionDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'question_detail.html'
    model = Question

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer_list'] = Answer.objects.filter(question=self.kwargs['pk'])

        like_for_question = LikeForQuestion.objects.filter(target=self.kwargs['pk'])
        context['like_for_question_count'] = like_for_question.count()
        if like_for_question.filter(user=self.request.user).exists():
            context['is_user_liked_for_question'] = True
        else:
            context['is_user_liked_for_question'] = False
        return context


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question_create.html'
    form_class = QuestionCreateForm
    success_url = reverse_lazy('qa:qa')

    def form_valid(self, form):
        question = form.save(commit=False)
        # ???????????????????????????ID?????????
        question.user = self.request.user
        # ????????????????????????????????????
        deadline = dt.datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=8)
        question.deadline = deadline
        question.save()

        messages.success(self.request, '??????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '???????????????????????????????????????')
        return super().form_invalid(form)


class AddSupplementView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'add_supplement.html'
    model = Question
    fields = ['supplement']

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        messages.success(self.request, '??????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '???????????????????????????????????????')
        return super().form_invalid(form)


@login_required
def question_delete_view(request, *args, **kwargs):
    question = Question.objects.get(pk=kwargs['pk'])
    question.delete()
    messages.success(request, '??????????????????????????????')
    return HttpResponseRedirect(reverse_lazy('qa:qa'))


class AnswerCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'answer_create.html'
    form_class = AnswerCreateForm
    success_url = reverse_lazy('qa:qa')

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        answer = form.save(commit=False)
        # ???????????????????????????ID?????????
        answer.user = self.request.user
        # question???ID?????????
        answer.question = Question.objects.get(pk=self.kwargs['pk'])
        answer.save()

        question = Question.objects.get(pk=self.kwargs['pk'])
        if not question.is_answered:
            question.is_answered = True
            question.save()

        messages.success(self.request, '??????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '???????????????????????????????????????')
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

        messages.success(self.request, '?????????????????????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '?????????????????????????????????????????????')
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

        messages.success(self.request, '?????????????????????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '??????????????????????????????????????????????????????')
        return super().form_invalid(form)
