from django import forms
from .models import StudyTime, Goal, Subject


class StudyTimeForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', required=True, queryset=Subject.objects.none())

    # ログインユーザーの教科を選択肢にする
    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user, is_disable=False)
        super().__init__(*args, **kwargs)

    class Meta:
        model = StudyTime
        fields = ['subject', 'studied_at', 'minutes']


class GoalCreateForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', required=False, queryset=Subject.objects.none())

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
        fields = ['name', 'color']
