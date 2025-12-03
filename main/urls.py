from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('grades/', views.grades_view, name='grades'),

    path('course/<int:pk>/', views.course_detail, name='course_detail'),

    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/grades/', views.teacher_grades, name='teacher_grades'),
    path('teacher/schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('teacher/ai-analysis/<int:student_id>/<int:course_id>/', views.ai_analysis_view, name='ai_analysis'),

    # Публичные академические страницы
    path('groups/<int:group_id>/schedule/', views.group_schedule, name='group_schedule'),
    path('students/<int:pk>/profile/', views.student_public_profile, name='student_public_profile'),
    path('courses/<int:pk>/lectures/', views.course_lectures, name='course_lectures'),
    path('lectures/<int:pk>/', views.lecture_detail, name='lecture_detail'),
    path('demo/', views.demo_page, name='demo_page'),

    # API для ML
    path('api/predict_grade/', views.api_predict_grade, name='api_predict_grade'),
    path('api/search_resources/', views.api_search_resources, name='api_search_resources'),
    path('api/retrain_embeddings/', views.api_retrain_embeddings, name='api_retrain_embeddings'),
]
