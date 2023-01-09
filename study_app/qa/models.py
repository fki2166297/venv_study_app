from django.db import models
from accounts.models import CustomUser

# Create your models here.
class SubjectChoices(models.TextChoices):
    NONE = '', '---------'
    JAPANESE = 'japanese', '国語'
    ENGLISH = 'english', '英語'
    MATH = 'math', '数学'
    PHYSICS = 'physics', '物理'
    CHEMISTRY = 'chemistry', '化学'
    BIOLOGY = 'biology', '生物'
    GEOLOGY = 'geology', '地学'
    INFORMATICS = 'informatics', '情報'
    HISTORY = 'history', '歴史'
    GEOGRAPHY = 'geography', '地理'
    CIVICS = 'civics', '公民'
    ART = 'art', '美術'


class Question(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    is_resolved = models.BooleanField(verbose_name='解決済み', default=False)
    is_answered = models.BooleanField(verbose_name='回答済み', default=False)
    subject = models.CharField(verbose_name='教科', choices=SubjectChoices.choices, max_length=30)
    image = models.ImageField(verbose_name='画像', upload_to='question_images/', null=True, blank=True, default='')
    title = models.CharField(verbose_name='タイトル', max_length=200)
    text = models.TextField(verbose_name='質問文')
    text_self_resolution = models.TextField(verbose_name='自己解決', blank=True)
    supplement = models.TextField(verbose_name='補足', blank=True)
    deadline = models.DateTimeField(verbose_name='締め切り')
    comment = models.TextField(verbose_name='お礼コメント', blank=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Question'

    def __str__(self):
        return self.text

# 質問に対するいいね
class LikeForQuestion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    target = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name='質問', on_delete=models.PROTECT)
    text = models.TextField(verbose_name='回答文')
    image = models.ImageField(verbose_name='画像', upload_to='answer_images/', null=True, blank=True, default='')
    is_best = models.BooleanField(verbose_name='ベストアンサー', default=False)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Answer'
