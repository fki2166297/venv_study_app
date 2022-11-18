from django import forms
from .models import Question, Answer, SubjectChoices


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
