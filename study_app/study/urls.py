from django.urls import path
from . import views


app_name = 'study'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('report', views.ReportView.as_view(), name='report'),
    path('qa', views.QuestionAndAnswerView.as_view(), name='qa'),
    path('qa/question-create', views.QuestionCreateView.as_view(), name='question_create'),
    path('qa/question-detail/<int:pk>', views.QuestionDetailView.as_view(), name='question_detail'),
    path('subject', views.SubjectView.as_view(), name='subject'),
    path('<slug:username>', views.AccountDetailView.as_view(), name='account_detail'),
    path('<slug:username>/follow', views.follow_view, name='follow'),
    path('<slug:username>/unfollow', views.unfollow_view, name='unfollow'),
]
