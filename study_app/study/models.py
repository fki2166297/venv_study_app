from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Subject(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    subject = models.CharField(verbose_name='教科', max_length=30)
    color = models.CharField(verbose_name='色', max_length=10)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Subject'

    def __str__(self):
        return self.subject


class StudyTime(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, verbose_name="教科", on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='開始日', null=False)
    start_time = models.TimeField(verbose_name='開始日', null=False)
    end_date = models.DateField(verbose_name='終了日', null=False)
    end_time = models.TimeField(verbose_name='終了日', null=False)
    study_minutes = models.IntegerField(verbose_name='学習時間', default=0)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'StudyTime'


class SubjectChoices(models.TextChoices):
    NONE = '', '---------'
    JAPANESE = 'japanese', '国語'
    MATH = 'math', '数学'
    SCIENCE = 'science', '科学'
    SOCIETY = 'society', '社会'
    ENGLISH = 'english', '英語'


class Question(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    is_answered = models.BooleanField(verbose_name='回答済み', default=False)
    subject = models.CharField(verbose_name='教科', choices=SubjectChoices.choices, max_length=15)
    image = models.ImageField(verbose_name='画像', upload_to='question_images/', null=True, blank=True, default='')
    text = models.TextField(verbose_name='質問文', blank=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Question'


class Answer(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name='質問', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='回答文', blank=True)
    image = models.ImageField(verbose_name='画像', upload_to='answer_images/', null=True, blank=True, default='')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Answer'
