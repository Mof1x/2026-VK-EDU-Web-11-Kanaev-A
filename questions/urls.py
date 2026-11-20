from django.urls import path

from . import ajax, views

app_name = 'questions'

urlpatterns = [
    path('', views.newest_questions, name='index'),
    path('hot/', views.hot_questions, name='hot'),
    path('tag/<str:tag>/', views.tagged_questions, name='tag'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
    path('question/<int:question_id>/vote/', ajax.question_vote, name='question_vote'),
    path('answer/<int:answer_id>/vote/', ajax.answer_vote, name='answer_vote'),
    path('question/<int:question_id>/accept/', ajax.accept_answer, name='accept_answer'),
    path('ask/', views.ask, name='ask'),
]
