from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from .models import Course, ScheduleEntry, Grade, Profile
from django.contrib.auth.forms import AuthenticationForm

def index(request):
    courses = Course.objects.all()[:6]
    return render(request, 'main/index.html', {'courses': courses})

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # ensure profile exists and set role/group
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data.get('role')
            profile.group = form.cleaned_data.get('group') or ''
            profile.save()
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

@login_required
def dashboard(request):
    # Основная студентская страница с кнопками
    user = request.user
    # Разделяем панели для студентов и преподавателей
    if hasattr(user, 'profile') and user.profile.role == Profile.ROLE_TEACHER:
        # перенаправить преподавателя на отдельную панель
        return redirect('teacher_dashboard')
    courses = Course.objects.all()
    upcoming = ScheduleEntry.objects.filter(student=user)[:6]
    recent_grades = Grade.objects.filter(student=user).order_by('-date')[:6]
    return render(request, 'main/dashboard.html', {
        'courses': courses,
        'upcoming': upcoming,
        'recent_grades': recent_grades
    })

@login_required
def schedule_view(request):
    user = request.user
    schedule = ScheduleEntry.objects.filter(student=user).order_by('weekday', 'start_time')
    return render(request, 'main/schedule.html', {'schedule': schedule})

@login_required
def grades_view(request):
    user = request.user
    grades = Grade.objects.filter(student=user).select_related('course').order_by('-date')
    return render(request, 'main/grades.html', {'grades': grades})

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
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # показать оценки и расписание по курсу для студента
    grades = Grade.objects.filter(student=request.user, course=course)
    schedule = ScheduleEntry.objects.filter(student=request.user, course=course)
    return render(request, 'main/course_detail.html', {'course': course, 'grades': grades, 'schedule': schedule})


# ===== Преподавательские разделы =====
def teacher_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or request.user.profile.role != Profile.ROLE_TEACHER:
            messages.error(request, 'Доступ только для преподавателей.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
@teacher_required
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'main/teacher_dashboard.html', {'courses': courses})


@login_required
@teacher_required
def teacher_courses(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'main/teacher_courses.html', {'courses': courses})


@login_required
@teacher_required
def teacher_grades(request):
    # Простая сводка оценок по курсам преподавателя
    grades = Grade.objects.filter(course__teacher=request.user).select_related('student', 'course').order_by('-date')
    return render(request, 'main/teacher_grades.html', {'grades': grades})


@login_required
@teacher_required
def teacher_schedule(request):
    schedule = ScheduleEntry.objects.filter(course__teacher=request.user).select_related('course').order_by('weekday', 'start_time')
    return render(request, 'main/teacher_schedule.html', {'schedule': schedule})
