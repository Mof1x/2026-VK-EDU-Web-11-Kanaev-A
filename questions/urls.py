from django.urls import path

from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.newest_questions, name='index'),
    path('hot/', views.hot_questions, name='hot'),
    path('tag/<str:tag>/', views.tagged_questions, name='tag'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
    path('ask/', views.AskView.as_view(), name='ask'),
]
