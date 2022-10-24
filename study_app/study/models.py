from django.db import models
from accounts.models import CustomUser
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Subject(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    subject = models.CharField(verbose_name='教科', max_length=30)
    color = models.CharField(verbose_name='色', max_length=10)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Subject'

    def __str__(self) -> str:
        return self.subject


class StudyTime(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, verbose_name="教科", on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='開始日')
    start_time = models.TimeField(verbose_name='開始時刻')
    study_minutes = models.IntegerField(verbose_name='学習時間', default=0, validators=[MinValueValidator(0)])
    end_date = models.DateField(verbose_name='終了日')
    end_time = models.TimeField(verbose_name='終了時刻')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'StudyTime'


class Question(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    is_answered = models.BooleanField(verbose_name='回答', default=False)
    subject = models.CharField(verbose_name='教科', max_length=30)
    image = models.ImageField(verbose_name='写真', blank=True)
    title = models.CharField(verbose_name='タイトル', max_length=40)
    text = models.TextField(verbose_name='質問文', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Question'


class Answer(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='回答文', blank=True, null=True)
    image = models.ImageField(verbose_name='写真', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Answer'
