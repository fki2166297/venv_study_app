from django import forms
from .models import StudyTime, Subject, Question, Answer
from django.db.models import TextChoices


class StudyTimeForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', required=True, queryset=Subject.objects.none())

    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user)
        super().__init__(*args, **kwargs)

    class Meta:
        model = StudyTime
        fields = ('subject', 'start_date', 'study_minutes', 'start_time', 'end_date', 'end_time')


class SubjectCreateForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('subject', 'color')


class SubjectChoices(TextChoices):
    ALL_SUBJECTS = 'all_subjects', '全教科'
    JAPANESE = 'japanese', '国語'
    MATH = 'math', '数学'
    SCIENCE = 'science', '科学'
    SOCIETY = 'society', '社会'
    ENGLISH = 'english', '英語'


class QuestionCreateForm(forms.ModelForm):
    subject = forms.fields.ChoiceField(label='教科の選択', required=False, choices=SubjectChoices.choices)

    class Meta:
        model = Question
        fields = ('subject', 'image', 'title', 'text')


class AnswerCreateForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text', 'image')
