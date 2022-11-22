from django.urls import path
from . import views


app_name = 'study'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('study-time-delete/<int:pk>', views.StudyTimeDeleteView.as_view(), name='study_time_delete'),
    path('study-time-update/<int:pk>', views.StudyTimeUpdateView.as_view(), name='study_time_update'),
    path('goal', views.GoalView.as_view(), name='goal'),
    path('goal-create', views.GoalCreateView.as_view(), name='goal_create'),
    path('report', views.ReportView.as_view(), name='report'),
    path('subject', views.SubjectView.as_view(), name='subject'),
    path('subject/subject-update/<int:pk>', views.SubjectUpdateView.as_view(), name='subject_update'),
    path('subject/subject-delete/<int:pk>', views.subject_delete_view, name='subject_delete'),
    path('<slug:username>', views.AccountDetailView.as_view(), name='account_detail'),
    path('<slug:username>/follow', views.follow_view, name='follow'),
    path('<slug:username>/unfollow', views.unfollow_view, name='unfollow'),
    path('<slug:username>/edit', views.AccountUpdateView.as_view(), name='account_update'),
]
