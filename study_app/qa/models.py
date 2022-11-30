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
    HEALTHANDPHYSICALEDUCATION = 'healthandphysicaleducation', '保健体育'
    TECHNICALHOMEECONOMICS = 'technicalhomeeconomics', '技術家庭科'
    ART = 'art', '美術'
    MUSIC = 'music', '音楽'
    ARTSANDCRAFTS = 'artsandcrafts', '図工'
    INFORMATION = 'information', '情報'
    CALLIGRAPHY = 'calligraphy', '書道'


class Question(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    is_resolved = models.BooleanField(verbose_name='解決済み', default=False)
    is_answered = models.BooleanField(verbose_name='回答済み', default=False)
    subject = models.CharField(verbose_name='教科', choices=SubjectChoices.choices, max_length=30)
    image = models.ImageField(verbose_name='画像', upload_to='question_images/', null=True, blank=True, default='')
    text = models.TextField(verbose_name='質問文')
    text_self_resolution = models.TextField(verbose_name='自己解決')
    supplement = models.TextField(verbose_name='補足', blank=True)
    deadline = models.DateTimeField(verbose_name='締め切り')
    comment = models.TextField(verbose_name='お礼コメント')
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

# # 回答に対するいいね
# class LikeForAnswer(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     target = models.ForeignKey(Answer, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
