from django.urls import path

from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.QuestionListView.as_view(), name='index'),
    path('hot/', views.HotQuestionListView.as_view(), name='hot'),
    path('tag/<str:tag>/', views.TagQuestionListView.as_view(), name='tag'),
    path('question/<int:question_id>/', views.QuestionDetailView.as_view(), name='question'),
    path('ask/', views.AskView.as_view(), name='ask'),
]
