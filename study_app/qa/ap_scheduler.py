from apscheduler.schedulers.background import BackgroundScheduler
import datetime as dt
from .models import Question


def delete_questions():
    now = dt.datetime.now()
    question = Question.objects.prefetch_related('answer').filter(deadline__lte=now)
    question.delete()
    print(question)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_questions, 'cron', minute=0)
    # scheduler.add_job(delete_questions, 'interval', seconds=5)
    scheduler.start()
