from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('grades/', views.grades_view, name='grades'),
    path('profile/', views.profile_view, name='profile'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    # teacher
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/grades/', views.teacher_grades, name='teacher_grades'),
    path('teacher/schedule/', views.teacher_schedule, name='teacher_schedule'),
]
