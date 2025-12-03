from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from functools import wraps
from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    TeacherGradeForm,
    LectureCreateForm,
)
from .models import (
    Profile,
    Course,
    Assignment,
    Submission,
    Recommendation,
    ScheduleEntry,
    Grade,
    Specialty,
    Subject,
    ProblemPrediction,
    StudentProgress,
    Group,
    Student,
    Lecture,
    Enrollment,
    Attendance,
)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .search_service import semantic_search

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
                group=form.cleaned_data.get('group'),
                specialty=form.cleaned_data.get('specialty'),
                enrollment_date=timezone.now().date()
                if form.cleaned_data['role'] == Profile.ROLE_STUDENT
                else None,
            )
            # Создаём сущность Student для студентов, чтобы связать с академическими моделями
            if form.cleaned_data['role'] == Profile.ROLE_STUDENT:
                Student.objects.get_or_create(
                    user=user,
                    defaults={
                        "first_name": user.first_name or user.username,
                        "last_name": user.last_name or "",
                        "email": user.email or f"{user.username}@example.com",
                        "group": form.cleaned_data.get('group'),
                    },
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
    # Стандартные роли
    if user.is_staff:
        # Возможные действия администратора/преподавателя
        from django.core.management import call_command

        if request.method == "POST":
            action = request.POST.get("action")
            if action == "seed_demo":
                call_command("seed_demo", students=500, groups=20, courses=30, seed=42)
                messages.success(request, "Демо-данные успешно сгенерированы.")
            elif action == "train_model":
                call_command("train_grade_model", save_path="models/grade_model.pkl")
                messages.success(request, "Модель прогноза оценок обучена.")
            elif action == "index_lectures":
                call_command("index_lectures")
                messages.success(request, "Индексация лекций выполнена.")
            return redirect("dashboard")

        # Админский/teacher дашборд с общей статистикой
        total_students = Student.objects.count()
        active_groups = Group.objects.count()
        total_courses = Course.objects.count()
        recent_enrollments = Enrollment.objects.select_related(
            "student", "course"
        ).order_by("-enrolled_at")[:10]
        return render(
            request,
            "main/dashboard.html",
            {
                "is_admin_dashboard": True,
                "total_students": total_students,
                "active_groups": active_groups,
                "total_courses": total_courses,
                "recent_enrollments": recent_enrollments,
            },
        )

    if hasattr(user, 'profile') and user.profile.role == Profile.ROLE_TEACHER:
        return redirect('teacher_dashboard')

    # Для студентов (личный кабинет)
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
        'is_admin_dashboard': False,
    })

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    assignments = Assignment.objects.filter(course=course)
    recommendations = Recommendation.objects.filter(submission__assignment__in=assignments)
    schedule = ScheduleEntry.objects.filter(course=course).order_by('weekday', 'start_time')
    
    # Получаем оценки для текущего пользователя (если студент) или все (если преподаватель)
    if hasattr(request.user, 'profile') and request.user.profile.role == Profile.ROLE_TEACHER:
        grades = Grade.objects.filter(course=course).select_related('student').order_by('-date')
    else:
        grades = Grade.objects.filter(course=course, student=request.user).order_by('-date')
    
    return render(request, 'main/course_detail.html', {
        'course': course,
        'assignments': assignments,
        'recommendations': recommendations,
        'schedule': schedule,
        'grades': grades,
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
    conditions = Q(groups__user=user)
    profile = getattr(user, "profile", None)
    if profile and profile.group:
        # Получаем профили студентов этой группы
        group_profiles = Profile.objects.filter(group=profile.group, role=Profile.ROLE_STUDENT)
        conditions |= Q(groups__in=group_profiles)
    schedule = (
        ScheduleEntry.objects.filter(conditions)
        .select_related("course")
        .distinct()
        .order_by("weekday", "start_time")
    )

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


# ===== Публичные академические страницы =====


def group_schedule(request, group_id: int):
    group = get_object_or_404(Group, id=group_id)
    # Получаем профили студентов этой группы
    group_profiles = Profile.objects.filter(group=group, role=Profile.ROLE_STUDENT)
    schedule = (
        ScheduleEntry.objects.filter(groups__in=group_profiles)
        .select_related("course")
        .distinct()
        .order_by("weekday", "start_time")
    )
    return render(
        request,
        "main/group_schedule.html",
        {
            "group": group,
            "schedule": schedule,
        },
    )


def student_public_profile(request, pk: int):
    student = get_object_or_404(Student, id=pk)
    enrollments = (
        Enrollment.objects.filter(student=student)
        .select_related("course")
        .order_by("course__name")
    )
    course_stats = []
    for enr in enrollments:
        grades_qs = Grade.objects.filter(enrollment=enr)
        attendance_qs = Attendance.objects.filter(enrollment=enr)
        attendance_rate = None
        if attendance_qs.exists():
            total = attendance_qs.count()
            present = attendance_qs.filter(present=True).count()
            attendance_rate = present * 100 / total if total else None

        avg_grade = grades_qs.aggregate(avg=Avg("value"))["avg"]
        course_stats.append(
            {
                "course": enr.course,
                "attendance_rate": attendance_rate,
                "avg_grade": avg_grade,
            }
        )

    return render(
        request,
        "main/student_public_profile.html",
        {
            "student_obj": student,
            "course_stats": course_stats,
        },
    )


def course_lectures(request, pk: int):
    course = get_object_or_404(Course, pk=pk)
    lectures = Lecture.objects.filter(course=course).order_by("created_at")
    q = request.GET.get("q", "").strip()
    search_results = None
    if q:
        search_results = semantic_search(q, top_k=5)
    return render(
        request,
        "main/course_lectures.html",
        {
            "course": course,
            "lectures": lectures,
            "q": q,
            "search_results": search_results,
        },
    )


def lecture_detail(request, pk: int):
    lecture = get_object_or_404(Lecture, pk=pk)
    related = semantic_search(lecture.title, top_k=5)
    return render(
        request,
        "main/lecture_detail.html",
        {
            "lecture": lecture,
            "related": related,
        },
    )


def demo_page(request):
    # Несколько случайных студентов и курсов для демонстрации
    students = Student.objects.all()[:10]
    courses = Course.objects.all()[:10]
    q = request.GET.get("q", "").strip()
    results = None
    if q:
        results = semantic_search(q, top_k=5)
    return render(
        request,
        "main/demo.html",
        {
            "students": students,
            "courses": courses,
            "q": q,
            "results": results,
        },
    )

# ===== Преподавательские страницы =====
@login_required
@teacher_required
def teacher_dashboard(request):
    user = request.user
    courses = Course.objects.filter(teacher=user).select_related('subject')
    grade_form = TeacherGradeForm(teacher=user)
    lecture_form = LectureCreateForm(teacher=user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_grade":
            grade_form = TeacherGradeForm(request.POST, teacher=user)
            if grade_form.is_valid():
                enrollment = grade_form.cleaned_data["enrollment"]
                student_user = getattr(enrollment.student, "user", None)
                if not student_user:
                    messages.error(
                        request,
                        "Для этого студента не найден профиль пользователя. Невозможно сохранить оценку.",
                    )
                else:
                    grade = grade_form.save(commit=False)
                    grade.course = enrollment.course
                    grade.student = student_user
                    grade.date = timezone.now()
                    grade.save()
                    messages.success(request, "Оценка успешно добавлена.")
                    return redirect("teacher_dashboard")
        elif action == "add_resource":
            lecture_form = LectureCreateForm(request.POST, teacher=user)
            if lecture_form.is_valid():
                lecture_form.save()
                messages.success(request, "Лекция/ресурс добавлены.")
                return redirect("teacher_dashboard")

    total_students = User.objects.filter(
        profile__role=Profile.ROLE_STUDENT,
        grades__course__teacher=user
    ).distinct().count()
    
    total_grades = Grade.objects.filter(course__teacher=user).count()
    avg_score = Grade.objects.filter(course__teacher=user).aggregate(avg=Avg('value'))['avg'] or 0
    
    recent_grades = Grade.objects.filter(course__teacher=user).select_related('student', 'course').order_by('-date')[:10]
    
    return render(request, 'main/teacher_dashboard.html', {
        'courses': courses,
        'total_students': total_students,
        'total_grades': total_grades,
        'avg_score': avg_score,
        'recent_grades': recent_grades,
        'grade_form': grade_form,
        'lecture_form': lecture_form,
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


# ===== API: ML прогноз и поиск =====


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)


@login_required
@staff_required
def api_predict_grade(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Только POST"}, status=405)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"detail": "Некорректный JSON"}, status=400)

    student_id = payload.get("student_id")
    course_id = payload.get("course_id")
    if not student_id or not course_id:
        return JsonResponse({"detail": "Нужно указать student_id и course_id"}, status=400)

    try:
        enrollment = Enrollment.objects.get(student_id=student_id, course_id=course_id)
    except Enrollment.DoesNotExist:
        return JsonResponse({"detail": "Запись студента на курс не найдена"}, status=404)

    # Загружаем модель
    from pathlib import Path

    model_path = Path("models/grade_model.pkl")
    if not model_path.exists():
        return JsonResponse({"detail": "Модель ещё не обучена. Запустите train_grade_model."}, status=503)

    import joblib  # type: ignore

    bundle = joblib.load(model_path)
    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    # Формируем признаки по той же логике, что и в train_grade_model
    grades_qs = Grade.objects.filter(enrollment=enrollment)
    from django.db.models import Avg

    att_qs = Attendance.objects.filter(enrollment=enrollment)
    attendance_rate = 1.0
    if att_qs.exists():
        total = att_qs.count()
        present = att_qs.filter(present=True).count()
        attendance_rate = present / total if total else 1.0

    hw_avg = grades_qs.filter(assignment_name__icontains="Домашнее").aggregate(
        avg=Avg("value")
    )["avg"]
    if hw_avg is None:
        hw_avg = grades_qs.exclude(assignment_name__icontains="Финал").aggregate(
            avg=Avg("value")
        )["avg"] or 0

    midterm = grades_qs.filter(assignment_name__icontains="Midterm").order_by(
        "-date"
    ).first()
    midterm_score = float(midterm.value) if midterm else float(hw_avg)

    previous_grades = Grade.objects.filter(
        student=enrollment.student.user if enrollment.student.user else None
    ).exclude(course=enrollment.course)
    if previous_grades.exists():
        previous_gpa = float(previous_grades.aggregate(avg=Avg("value"))["avg"] or 0)
    else:
        previous_gpa = float(hw_avg)

    features = [
        float(attendance_rate * 100.0),
        float(hw_avg),
        float(midterm_score),
        float(previous_gpa),
    ]

    x = scaler.transform([features])
    pred = float(model.predict(x)[0])

    # Простое объяснение: вклад признаков (для линейной модели)
    contributions = {}
    coef = getattr(model, "coef_", None)
    if coef is not None:
        for name, c, val in zip(feature_names, coef, features):
            contributions[name] = float(c * val)
        confidence = 0.8
    else:
        # Для деревьев используем feature_importances_
        importances = getattr(model, "feature_importances_", None)
        if importances is not None:
            for name, imp in zip(feature_names, importances):
                contributions[name] = float(imp)
            confidence = float(max(importances) if len(importances) else 0.5)
        else:
            confidence = 0.5

    return JsonResponse(
        {
            "predicted_final_grade": pred,
            "model_confidence": confidence,
            "feature_contributions": contributions,
        }
    )


def api_search_resources(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Только POST"}, status=405)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"detail": "Некорректный JSON"}, status=400)

    q = (payload.get("q") or "").strip()
    top_k = int(payload.get("top_k") or 5)
    top_k = max(1, min(top_k, 20))

    results = semantic_search(q, top_k=top_k)
    return JsonResponse({"results": results})


@login_required
@staff_required
def api_retrain_embeddings(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Только POST"}, status=405)
    from django.core.management import call_command

    call_command("index_lectures")
    return JsonResponse({"detail": "Индексация лекций запущена."})
