from django import forms
from .models import StudyTime, Goal, Subject, Question, Answer, SubjectChoices


class StudyTimeForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', required=True, queryset=Subject.objects.none())

    # ログインユーザーの教科を選択肢にする
    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user, is_disable=False)
        super().__init__(*args, **kwargs)

    class Meta:
        model = StudyTime
        fields = ['subject', 'studied_at', 'study_minutes']


class GoalCreateForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', required=True, queryset=Subject.objects.none())

    # ログインユーザーの教科を選択肢にする
    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Goal
        fields = ['subject', 'text', 'date', 'minutes']


class SubjectCreateForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject', 'color']


class SubjectSelectForm(forms.Form):
    subject = forms.fields.ChoiceField(label='教科の選択', required=False, choices=SubjectChoices.choices)


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'text', 'image']


class AnswerCreateForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'image']
