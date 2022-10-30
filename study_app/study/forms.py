from django import forms
from .models import StudyTime, Subject, Question, Answer
from django.db.models import TextChoices


class StudyTimeForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', required=True, queryset=Subject.objects.none())

    # ログインユーザーの教科を選択肢にする
    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user)
        super().__init__(*args, **kwargs)

    class Meta:
        model = StudyTime
        fields = ('subject', 'start_date', 'start_time', 'end_date', 'end_time')


class SubjectCreateForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('subject', 'color')


class SubjectChoices(TextChoices):
    JAPANESE = '国語', '国語'
    MATH = '数学', '数学'
    SCIENCE = '科学', '科学'
    SOCIETY = '社会', '社会'
    ENGLISH = '英語', '英語'


class QuestionCreateForm(forms.ModelForm):
    subject = forms.fields.ChoiceField(label='教科の選択', required=False, choices=SubjectChoices.choices)

    class Meta:
        model = Question
        fields = ('subject', 'text', 'image')


class AnswerCreateForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text', 'image')
