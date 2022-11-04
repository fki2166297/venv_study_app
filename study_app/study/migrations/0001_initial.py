# Generated by Django 4.1.1 on 2022-11-04 02:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=30, verbose_name='教科')),
                ('color', models.CharField(max_length=10, verbose_name='色')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name_plural': 'Subject',
            },
        ),
        migrations.CreateModel(
            name='StudyTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('studied_at', models.DateTimeField(verbose_name='日時')),
                ('study_minutes', models.IntegerField(default=0, verbose_name='学習時間')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='study.subject', verbose_name='教科')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name_plural': 'StudyTime',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_answered', models.BooleanField(default=False, verbose_name='回答済み')),
                ('subject', models.CharField(choices=[('', '---------'), ('japanese', '国語'), ('math', '数学'), ('science', '科学'), ('society', '社会'), ('english', '英語')], max_length=15, verbose_name='教科')),
                ('image', models.ImageField(blank=True, default='', null=True, upload_to='question_images/', verbose_name='画像')),
                ('text', models.TextField(blank=True, verbose_name='質問文')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name_plural': 'Question',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, verbose_name='回答文')),
                ('image', models.ImageField(blank=True, default='', null=True, upload_to='answer_images/', verbose_name='画像')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='study.question', verbose_name='質問')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name_plural': 'Answer',
            },
        ),
    ]
