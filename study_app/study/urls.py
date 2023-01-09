from django.urls import path
from . import views


app_name = 'study'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('studytime-create', views.StudyTimeCreateView.as_view(), name='studytime_create'),
    path('studytime-update/<int:pk>', views.StudyTimeUpdateView.as_view(), name='studytime_update'),
    path('studytime-delete/<int:pk>', views.StudyTimeDeleteView.as_view(), name='studytime_delete'),
    path('report', views.ReportView.as_view(), name='report'),
    path('subject', views.SubjectView.as_view(), name='subject'),
    path('subject-create', views.SubjectCreateView.as_view(), name='subject_create'),
    path('subject/subject-update/<int:pk>', views.SubjectUpdateView.as_view(), name='subject_update'),
    path('subject/subject-delete/<int:pk>', views.subject_delete_view, name='subject_delete'),
    path('account-search', views.AccountSearchView.as_view(), name='account_search'),
    path('check-username-exists', views.check_username_exists, name='check_username_exists'),
    path('<slug:username>', views.AccountDetailView.as_view(), name='account_detail'),
    path('<slug:username>/follow', views.follow_view, name='follow'),
    path('<slug:username>/unfollow', views.unfollow_view, name='unfollow'),
    path('<slug:username>/edit', views.AccountUpdateView.as_view(), name='account_update'),
]
