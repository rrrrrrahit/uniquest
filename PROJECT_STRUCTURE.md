# UniQuest - Структура проекта и документация

## 📁 Дерево проекта

```
uniquest/
├── main/                          # Основное приложение
│   ├── __init__.py
│   ├── admin.py                   # Настройки админ-панели Django
│   ├── apps.py                    # Конфигурация приложения
│   ├── models.py                  # Модели базы данных (полный код ниже)
│   ├── views.py                   # Представления (views) - логика приложения
│   ├── forms.py                   # Формы для регистрации и редактирования
│   ├── urls.py                    # URL маршруты приложения
│   ├── signals.py                 # Сигналы Django
│   ├── search_service.py          # Сервис семантического поиска
│   ├── ml_service.py              # ML сервисы для анализа
│   ├── templates/                 # HTML шаблоны
│   │   └── main/
│   │       ├── base.html
│   │       ├── index.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── dashboard.html
│   │       ├── profile.html
│   │       ├── course_detail.html
│   │       ├── grades.html
│   │       ├── schedule.html
│   │       ├── teacher_dashboard.html
│   │       └── ...
│   ├── static/                    # Статические файлы (CSS, JS, изображения)
│   │   └── main/
│   │       ├── css/
│   │       ├── js/
│   │       └── images/
│   ├── migrations/                # Миграции базы данных
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_scheduleentry_options...
│   │   └── ...
│   └── management/                # Команды управления
│       └── commands/
│           ├── seed_demo.py       # Генерация демо-данных
│           ├── train_grade_model.py  # Обучение ML модели
│           └── index_lectures.py     # Индексация лекций
│
├── uniquest/                      # Настройки проекта Django
│   ├── __init__.py
│   ├── settings.py               # Настройки проекта (полный код ниже)
│   ├── urls.py                   # Главные URL маршруты
│   ├── wsgi.py                   # WSGI конфигурация для деплоя
│   └── signals.py
│
├── manage.py                     # Управляющий скрипт Django
├── requirements.txt              # Зависимости Python
├── Procfile                      # Конфигурация для деплоя
├── render.yaml                   # Конфигурация для Render.com
├── runtime.txt                   # Версия Python
├── .gitignore                    # Игнорируемые файлы Git
└── README.md                     # Основная документация
```

---

## 🗄️ Модели базы данных (main/models.py)

### Полный код основных моделей:

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# ----------------- Specialty (Специальность) -----------------
class Specialty(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Код специальности')
    name_kk = models.CharField(max_length=200, verbose_name='Название (каз)')
    name_ru = models.CharField(max_length=200, verbose_name='Название (рус)')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name_ru}"

# ----------------- Subject (Предмет) -----------------
class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Код предмета')
    name_kk = models.CharField(max_length=200, verbose_name='Название (каз)')
    name_ru = models.CharField(max_length=200, verbose_name='Название (рус)')
    credits = models.IntegerField(default=3, verbose_name='Кредиты')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, null=True, blank=True, related_name='subjects')

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name_ru}"

# ----------------- Group (Группа) -----------------
class Group(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Группа")
    year = models.IntegerField(verbose_name="Год набора")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ["-year", "name"]

    def __str__(self):
        return f"{self.name} ({self.year})"

# ----------------- Profile (Профиль пользователя) -----------------
class Profile(models.Model):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Студент'),
        (ROLE_TEACHER, 'Преподаватель'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    iin = models.CharField(max_length=12, blank=True)
    address = models.TextField(blank=True)
    enrollment_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

# ----------------- Course (Курс) -----------------
class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_courses')
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    semester = models.IntegerField(choices=[(1, 'Осенний'), (2, 'Весенний')], default=1)
    academic_year = models.CharField(max_length=9, default='2024-2025')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-academic_year', 'semester', 'code']

    def __str__(self):
        return f"{self.code or ''} {self.name}".strip()

# ----------------- Student (Студент) -----------------
class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_profile')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_group')
    dob = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

# ----------------- Enrollment (Запись на курс) -----------------
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(default=timezone.now, verbose_name='Дата записи')

    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        ordering = ['-enrolled_at']
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student} - {self.course.name}"

# ----------------- Lecture (Лекция) -----------------
class Lecture(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=200, verbose_name='Название')
    content_text = models.TextField(blank=True, verbose_name='Содержание')
    content_url = models.URLField(blank=True, null=True, verbose_name='Ссылка')
    vector_embedding = models.JSONField(null=True, blank=True, verbose_name='Векторное представление')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Лекция'
        verbose_name_plural = 'Лекции'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.name} - {self.title}"

# ----------------- Grade (Оценка) -----------------
class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.SET_NULL, null=True, blank=True, related_name='grades')
    assignment = models.ForeignKey('Assignment', on_delete=models.SET_NULL, null=True, blank=True, related_name='grades')
    assignment_name = models.CharField(max_length=200, blank=True, verbose_name='Название задания')
    value = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    letter_grade = models.CharField(max_length=5, choices=[('A','A'),('B','B'),('C','C'),('D','D'),('F','F')], blank=True)
    date = models.DateTimeField(default=timezone.now)
    comment = models.TextField(blank=True)
    topic = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # Автоматически заполняем assignment_name из assignment, если не указано
        if self.assignment and not self.assignment_name:
            self.assignment_name = self.assignment.title
        # Автоматически заполняем student из enrollment, если не указано
        if self.enrollment and not self.student:
            self.student = self.enrollment.student.user if self.enrollment.student.user else None
        if self.value is not None and not self.letter_grade:
            if self.value >= 90: self.letter_grade='A'
            elif self.value >= 80: self.letter_grade='B'
            elif self.value >= 70: self.letter_grade='C'
            elif self.value >= 60: self.letter_grade='D'
            else: self.letter_grade='F'
        super().save(*args, **kwargs)

    def __str__(self):
        student_name = self.student.username if self.student else (self.enrollment.student if self.enrollment else "Неизвестно")
        return f"{student_name} - {self.course.name} - {self.value}"

# ----------------- Assignment (Задание) -----------------
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    max_score = models.IntegerField(default=100)
    topic = models.CharField(max_length=200, blank=True)
    assignment_type = models.CharField(
        max_length=50,
        choices=[
            ('homework', 'Домашнее задание'),
            ('project', 'Проект'),
            ('quiz', 'Контрольная работа'),
            ('exam', 'Экзамен'),
            ('lab', 'Лабораторная работа')
        ],
        default='homework'
    )

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.course.name} - {self.title}"

# ----------------- Attendance (Посещаемость) -----------------
class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendances')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)
    date = models.DateField(verbose_name='Дата')
    present = models.BooleanField(default=False, verbose_name='Присутствовал')

    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        ordering = ['-date']
        unique_together = ['enrollment', 'lecture', 'date']

    def __str__(self):
        status = "Присутствовал" if self.present else "Отсутствовал"
        return f"{self.enrollment.student} - {self.date} - {status}"
```

---

## 🎯 Основные представления (main/views.py)

### Ключевые функции:

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from functools import wraps

# Главная страница
def index(request):
    courses = Course.objects.all()[:6]
    return render(request, 'main/index.html', {'courses': courses})

# Регистрация
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

# Декоратор для проверки роли преподавателя
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

# Декоратор для проверки роли студента
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

# Панель пользователя
@login_required
def dashboard(request):
    user = request.user
    if user.is_staff:
        # Админский дашборд
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
        'is_admin_dashboard': False,
    })

# Панель преподавателя
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
                    messages.error(request, "Для этого студента не найден профиль пользователя.")
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

# API для ML прогноза оценки
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

    # Загрузка обученной модели
    from pathlib import Path
    model_path = Path("models/grade_model.pkl")
    if not model_path.exists():
        return JsonResponse({"detail": "Модель ещё не обучена."}, status=503)

    import joblib
    bundle = joblib.load(model_path)
    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    # Формирование признаков
    grades_qs = Grade.objects.filter(enrollment=enrollment)
    att_qs = Attendance.objects.filter(enrollment=enrollment)
    
    # Расчет признаков для прогноза
    attendance_rate = 1.0
    if att_qs.exists():
        total = att_qs.count()
        present = att_qs.filter(present=True).count()
        attendance_rate = present / total if total else 1.0

    hw_avg = grades_qs.filter(assignment_name__icontains="Домашнее").aggregate(avg=Avg("value"))["avg"] or 0
    midterm = grades_qs.filter(assignment_name__icontains="Midterm").order_by("-date").first()
    midterm_score = float(midterm.value) if midterm else float(hw_avg)

    previous_grades = Grade.objects.filter(
        student=enrollment.student.user if enrollment.student.user else None
    ).exclude(course=enrollment.course)
    previous_gpa = float(previous_grades.aggregate(avg=Avg("value"))["avg"] or 0) if previous_grades.exists() else float(hw_avg)

    features = [
        float(attendance_rate * 100.0),
        float(hw_avg),
        float(midterm_score),
        float(previous_gpa),
    ]

    x = scaler.transform([features])
    pred = float(model.predict(x)[0])

    return JsonResponse({
        "predicted_final_grade": pred,
        "model_confidence": 0.8,
        "feature_contributions": {
            "attendance": float(attendance_rate * 100),
            "homework_avg": float(hw_avg),
            "midterm": float(midterm_score),
            "previous_gpa": float(previous_gpa),
        }
    })
```

---

## ⚙️ Настройки проекта (uniquest/settings.py)

### Полный код настроек:

```python
import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# --- ПУТИ ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- БЕЗОПАСНОСТЬ ---
SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# --- ALLOWED_HOSTS ---
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]
else:
    ALLOWED_HOSTS = ['*']

# Автоматическое добавление хостов Render
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_host:
    if render_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(render_host)
    if '*.onrender.com' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('*.onrender.com')

# Безопасность для production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# --- УСТАНОВЛЕННЫЕ ПРИЛОЖЕНИЯ ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

# --- МИДЛВАР ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'uniquest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'uniquest.wsgi.application'

# --- БАЗА ДАННЫХ ---
# Приоритет: DATABASE_URL (от Render) > отдельные переменные > значения по умолчанию
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'uniquestus'),
        'USER': os.environ.get('DB_USER', 'uniquest_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,
    }
}

# Использование DATABASE_URL от Render (приоритет)
if 'DATABASE_URL' in os.environ:
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    except ImportError:
        # Если dj-database-url не установлен, парсим вручную
        import urllib.parse
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            parsed = urllib.parse.urlparse(db_url)
            DATABASES['default'] = {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': parsed.path[1:] if parsed.path.startswith('/') else parsed.path,
                'USER': parsed.username,
                'PASSWORD': parsed.password,
                'HOST': parsed.hostname,
                'PORT': parsed.port or '5432',
                'OPTIONS': {
                    'connect_timeout': 10,
                },
                'CONN_MAX_AGE': 600,
            }

# --- ПАРОЛИ ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- ЛОКАЛЬНЫЕ НАСТРОЙКИ ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- СТАТИКА ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- МЕДИА ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## 🔗 URL маршруты

### Главные маршруты (uniquest/urls.py):

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]

# Для раздачи медиа файлов в development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### Маршруты приложения (main/urls.py):

```python
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
```

---

## 📝 Формы (main/forms.py)

### Основные формы:

```python
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Specialty, Grade, Enrollment, Course, Lecture, Group

# Регистрация пользователя
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=False, label='Имя')
    last_name = forms.CharField(required=False, label='Фамилия')
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label='Роль')
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Группа',
        help_text='Учебная группа (для студентов)'
    )
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        label='Специальность',
        help_text='Выберите специальность (для студентов)'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'group', 'specialty', 'password1', 'password2']
        labels = {'username': 'Логин'}

# Форма выставления оценки преподавателем
class TeacherGradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['enrollment', 'assignment', 'value', 'topic', 'comment']
        labels = {
            'enrollment': 'Студент и курс',
            'assignment': 'Задание',
            'value': 'Балл',
            'topic': 'Тема',
            'comment': 'Комментарий',
        }
        widgets = {'comment': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher
        qs = Enrollment.objects.select_related('student__user', 'course')
        if teacher:
            qs = qs.filter(course__teacher=teacher)
        self.fields['enrollment'].queryset = qs
        self.fields['enrollment'].label_from_instance = lambda enr: f"{enr.student.last_name} {enr.student.first_name} — {enr.course.name}"

# Создание лекции/ресурса
class LectureCreateForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['course', 'title', 'content_text', 'content_url']
        labels = {
            'course': 'Курс',
            'title': 'Название лекции/ресурса',
            'content_text': 'Содержание',
            'content_url': 'Ссылка (необязательно)',
        }
        widgets = {'content_text': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Course.objects.all()
        if teacher:
            qs = qs.filter(teacher=teacher)
        self.fields['course'].queryset = qs
```

---

## 🛠️ Технологии и зависимости

### Основные технологии:

- **Django 5.2.7** - веб-фреймворк
- **PostgreSQL** - база данных
- **Python 3.13** - язык программирования
- **Bootstrap 5** - CSS фреймворк
- **Gunicorn** - WSGI сервер для production
- **WhiteNoise** - обработка статических файлов

### ML/AI библиотеки:

- **scikit-learn** - машинное обучение
- **numpy** - численные вычисления
- **sentence-transformers** - семантический поиск
- **torch** - глубокое обучение
- **joblib** - сохранение моделей

### Основные зависимости (requirements.txt):

```
Django==5.2.7
gunicorn==23.0.0
psycopg2-binary==2.9.11
dj-database-url==3.0.1
whitenoise==6.11.0
python-dotenv==1.2.1
numpy
scikit-learn
joblib
sentence-transformers
rank-bm25
```

---

## 🚀 Развертывание на Render

### Конфигурация (render.yaml):

```yaml
services:
  - type: web
    name: uniquest-web
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
    startCommand: python manage.py migrate --noinput && gunicorn uniquest.wsgi:application
    healthCheckPath: /
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.12
      - key: DJANGO_SETTINGS_MODULE
        value: uniquest.settings
      - key: DEBUG
        value: False
      - key: SECRET_KEY
        generateValue: true
      - key: ALLOWED_HOSTS
        value: uniquest.onrender.com,*.onrender.com
      - key: DATABASE_URL
        fromDatabase:
          name: uniquest1-db
          property: connectionString
```

---

## 📊 Основные функции системы

### Для студентов:
- Регистрация и авторизация
- Просмотр расписания
- Просмотр оценок и статистики
- Просмотр курсов и лекций
- Семантический поиск по материалам

### Для преподавателей:
- Панель управления курсами
- Выставление оценок
- Добавление лекций и материалов
- Просмотр статистики студентов
- AI анализ успеваемости

### Для администраторов:
- Полный доступ к админ-панели
- Генерация демо-данных
- Обучение ML моделей
- Индексация лекций

---

## 🔐 Безопасность

- Использование переменных окружения для секретных ключей
- CSRF защита
- XSS защита
- SSL редирект в production
- Разделение доступа по ролям (студент/преподаватель/админ)

---

## 📈 ML/AI функции

1. **Прогноз итоговой оценки** - на основе посещаемости, домашних заданий, midterm и предыдущего GPA
2. **Семантический поиск** - поиск по лекциям с использованием embeddings
3. **Анализ успеваемости** - выявление проблемных тем и рекомендации

---

## 📝 Команды управления

```bash
# Генерация демо-данных
python manage.py seed_demo --students 500 --groups 20 --courses 30

# Обучение модели прогноза оценок
python manage.py train_grade_model --save-path=models/grade_model.pkl

# Индексация лекций для поиска
python manage.py index_lectures
```

---

## 🌐 URL структура

- `/` - главная страница
- `/register/` - регистрация
- `/login/` - вход
- `/dashboard/` - панель пользователя
- `/course/<id>/` - детали курса
- `/teacher/dashboard/` - панель преподавателя
- `/api/predict_grade/` - API прогноза оценки
- `/api/search_resources/` - API поиска

---

**Проект создан для образовательных целей.**
**Версия:** 1.0
**Дата:** Декабрь 2025

