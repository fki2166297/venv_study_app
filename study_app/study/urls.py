from django.urls import path
from . import views


app_name = 'study'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('study-time-update/<int:pk>', views.StudyTimeUpdateView.as_view(), name='study-time-update'),
    path('study-time-delete/<int:pk>', views.StudyTimeDeleteView.as_view(), name='study-time-delete'),
    path('report', views.ReportView.as_view(), name='report'),
    path('qa', views.QuestionAndAnswerView.as_view(), name='qa'),
    path('qa/question-detail/<int:pk>', views.QuestionDetailView.as_view(), name='question-detail'),
    path('qa/question-create', views.QuestionCreateView.as_view(), name='question-create'),
    path('subject', views.SubjectView.as_view(), name='subject'),
    path('my-page/<int:pk>', views.MyPageView.as_view(), name='my-page'),
]
