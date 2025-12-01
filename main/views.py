from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import (
    Profile, Course, Assignment, Submission, Recommendation, 
    ScheduleEntry, Grade, Specialty, Subject, ProblemPrediction, 
    StudentProgress
)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
import json

# ===== Главная и авторизация =====
def index(request):
    courses = Course.objects.all()[:6]
    return render(request, 'main/index.html', {'courses': courses})

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile.objects.create(
                user=user, 
                role=form.cleaned_data['role'], 
                group=form.cleaned_data.get('group', ''),
                specialty=form.cleaned_data.get('specialty'),
                enrollment_date=timezone.now().date() if form.cleaned_data['role'] == Profile.ROLE_STUDENT else None
            )
            login(request, user)
            messages.success(request, 'Регистрация успешна. Добро пожаловать!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Ошибка входа. Проверьте логин и пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('index')

# ===== Декораторы доступа =====
def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or request.user.profile.role != Profile.ROLE_TEACHER:
            messages.error(request, 'Доступ только для преподавателей.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped

def student_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or request.user.profile.role != Profile.ROLE_STUDENT:
            messages.error(request, 'Доступ только для студентов.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped

# ===== Панель пользователя =====
@login_required
def dashboard(request):
    user = request.user
    if hasattr(user, 'profile') and user.profile.role == Profile.ROLE_TEACHER:
        return redirect('teacher_dashboard')
    
    # Для студентов
    courses = Course.objects.all()
    user_grades = Grade.objects.filter(student=user).select_related('course')
    avg_score = user_grades.aggregate(avg=Avg('value'))['avg'] or 0
    
    recent_grades = user_grades[:5]
    upcoming_assignments = Assignment.objects.filter(
        course__in=courses,
        due_date__gte=timezone.now()
    ).order_by('due_date')[:5]
    
    return render(request, 'main/dashboard.html', {
        'courses': courses,
        'user_grades': user_grades,
        'avg_score': avg_score,
        'recent_grades': recent_grades,
        'upcoming_assignments': upcoming_assignments,
    })

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    assignments = Assignment.objects.filter(course=course)
    recommendations = Recommendation.objects.filter(submission__assignment__in=assignments)
    return render(request, 'main/course_detail.html', {
        'course': course,
        'assignments': assignments,
        'recommendations': recommendations
    })

@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'main/profile.html', {'u_form': u_form, 'p_form': p_form})

@login_required
@student_required
def schedule_view(request):
    user = request.user
    # Получаем расписание для групп студента
    schedule = ScheduleEntry.objects.filter(
        groups__user=user
    ).distinct().order_by('weekday', 'start_time')
    
    return render(request, 'main/schedule.html', {'schedule': schedule})

@login_required
@student_required
def grades_view(request):
    user = request.user
    grades = Grade.objects.filter(student=user).select_related('course', 'assignment').order_by('-date')
    
    # Статистика
    total_grades = grades.count()
    avg_score = grades.aggregate(avg=Avg('value'))['avg'] or 0
    courses_stats = {}
    
    for grade in grades:
        if grade.course.id not in courses_stats:
            courses_stats[grade.course.id] = {
                'course': grade.course,
                'grades': [],
                'avg': 0
            }
        courses_stats[grade.course.id]['grades'].append(grade.value)
    
    for course_id, stats in courses_stats.items():
        stats['avg'] = sum(stats['grades']) / len(stats['grades'])
    
    return render(request, 'main/grades.html', {
        'grades': grades,
        'total_grades': total_grades,
        'avg_score': avg_score,
        'courses_stats': courses_stats.values(),
    })

# ===== Преподавательские страницы =====
@login_required
@teacher_required
def teacher_dashboard(request):
    user = request.user
    courses = Course.objects.filter(teacher=user).select_related('subject')
    
    # Статистика
    total_students = User.objects.filter(
        profile__role=Profile.ROLE_STUDENT,
        grades__course__teacher=user
    ).distinct().count()
    
    total_grades = Grade.objects.filter(course__teacher=user).count()
    avg_score = Grade.objects.filter(course__teacher=user).aggregate(avg=Avg('value'))['avg'] or 0
    
    # Недавние оценки
    recent_grades = Grade.objects.filter(course__teacher=user).select_related('student', 'course').order_by('-date')[:10]
    
    return render(request, 'main/teacher_dashboard.html', {
        'courses': courses,
        'total_students': total_students,
        'total_grades': total_grades,
        'avg_score': avg_score,
        'recent_grades': recent_grades,
    })

@login_required
@teacher_required
def teacher_courses(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'main/teacher_courses.html', {'courses': courses})

@login_required
@teacher_required
def teacher_grades(request):
    grades = Grade.objects.filter(course__teacher=request.user).select_related('student', 'course').order_by('-date')
    return render(request, 'main/teacher_grades.html', {'grades': grades})

@login_required
@teacher_required
def teacher_schedule(request):
    schedule = ScheduleEntry.objects.filter(
        course__teacher=request.user
    ).select_related('course').prefetch_related('groups').order_by('weekday', 'start_time')
    return render(request, 'main/teacher_schedule.html', {'schedule': schedule})

# ===== ML/AI функции для оценивания =====
def analyze_student_performance(student, course):
    """Анализирует успеваемость студента и предсказывает проблемные темы"""
    grades = Grade.objects.filter(student=student, course=course)
    
    if not grades.exists():
        return None
    
    # Простой алгоритм анализа
    topics = {}
    for grade in grades:
        if grade.topic:
            if grade.topic not in topics:
                topics[grade.topic] = []
            topics[grade.topic].append(float(grade.value))
    
    problem_areas = []
    recommendations = []
    
    for topic, scores in topics.items():
        avg_score = sum(scores) / len(scores)
        if avg_score < 60:
            problem_areas.append({
                'topic': topic,
                'avg_score': avg_score,
                'severity': 'high' if avg_score < 50 else 'medium'
            })
            recommendations.append(f"Рекомендуется дополнительная работа по теме '{topic}'")
    
    return {
        'problem_areas': problem_areas,
        'recommendations': recommendations,
        'overall_avg': grades.aggregate(avg=Avg('value'))['avg'] or 0
    }

@login_required
@teacher_required
def ai_analysis_view(request, student_id, course_id):
    """Страница с анализом студента через ИИ"""
    student = get_object_or_404(User, id=student_id)
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    
    analysis = analyze_student_performance(student, course)
    progress_records = StudentProgress.objects.filter(student=student, course=course).order_by('-created_at')
    
    return render(request, 'main/ai_analysis.html', {
        'student': student,
        'course': course,
        'analysis': analysis,
        'progress_records': progress_records,
    })
