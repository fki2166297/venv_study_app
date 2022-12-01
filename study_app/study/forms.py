from django import forms
from django.db import models
from .models import StudyTime, Goal, Subject


class StudyTimeForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', queryset=Subject.objects.none())

    # ログインユーザーの教科を選択肢にする
    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user, is_available=True)
        super().__init__(*args, **kwargs)

    class Meta:
        model = StudyTime
        fields = ['subject', 'studied_at', 'minutes', 'publication']


class GoalCreateForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', required=False, queryset=Subject.objects.none())

    # ログインユーザーの教科を選択肢にする
    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Goal
        fields = ['subject', 'datetime', 'goal_minutes']


class SubjectCreateForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'color']
