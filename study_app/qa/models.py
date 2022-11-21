from django.db import models
from accounts.models import CustomUser

# Create your models here.
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
    supplement = models.TextField(verbose_name='補足', blank=True)
    deadline = models.DateTimeField(verbose_name='締め切り')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Question'

# 質問に対するいいね
class LikeForQuestion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    target = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name='質問', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='回答文', blank=True)
    image = models.ImageField(verbose_name='画像', upload_to='answer_images/', null=True, blank=True, default='')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Answer'

# # 回答に対するいいね
# class LikeForAnswer(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     target = models.ForeignKey(Answer, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)