from django.urls import path
from . import views


app_name = 'qa'
urlpatterns = [
    path('', views.QuestionAndAnswerView.as_view(), name='qa'),
    path('question-detail/<int:pk>', views.QuestionDetailView.as_view(), name='question_detail'),
    path('question-create', views.QuestionCreateView.as_view(), name='question_create'),
    path('question-update/<int:pk>', views.QuestionUpdateView.as_view(), name='question_update'),
    path('like_for_question', views.like_for_question, name='like_for_question'),
]