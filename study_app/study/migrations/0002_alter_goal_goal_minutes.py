# Generated by Django 4.1.1 on 2022-11-21 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='goal_minutes',
            field=models.IntegerField(default=15, verbose_name='目標学習時間'),
        ),
    ]