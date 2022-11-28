from apscheduler.schedulers.background import BackgroundScheduler
import datetime as dt
from .models import Question


def delete_questions():
    now = dt.datetime.now().astimezone()
    print(now)
    questions = Question.objects.filter(deadline__lte=now, is_resolved=False, is_answered=False)
    if questions.exists():
        deadline = now.replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=8)
        for question in questions:
            question.deadline = deadline
        # 質問の締切日時を一括更新
        Question.objects.bulk_update(questions, fields=['deadline'])

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_questions, 'cron',  hour=0) # 毎日0時に実行
    scheduler.start()
