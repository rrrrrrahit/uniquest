from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# ----------------- Specialty -----------------
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

# ----------------- Subject -----------------
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

# ----------------- Group -----------------
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

# ----------------- Profile -----------------
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

# ----------------- Course -----------------
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

# ----------------- Assignment -----------------
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

# ----------------- Submission -----------------
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Работа студента'
        verbose_name_plural = 'Работы студентов'
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

# ----------------- ProblemPrediction -----------------
class ProblemPrediction(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='prediction')
    predicted_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    difficulty_level = models.CharField(max_length=20, choices=[('low','Низкая'),('medium','Средняя'),('high','Высокая')], blank=True)
    problem_areas = models.JSONField(default=list)
    recommendations = models.TextField(blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Прогноз проблем'
        verbose_name_plural = 'Прогнозы проблем'

    def __str__(self):
        return f"Прогноз для {self.submission.student.username}"

# ----------------- StudentProgress -----------------
class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress')
    topic = models.CharField(max_length=200)
    understanding_level = models.IntegerField(choices=[(1,'Плохо'),(2,'Удовлетворительно'),(3,'Хорошо'),(4,'Отлично')])
    issues = models.JSONField(default=list)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Прогресс студента'
        verbose_name_plural = 'Прогресс студентов'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.name} - {self.topic}"

# ----------------- Recommendation -----------------
class Recommendation(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='recommendations')
    text = models.TextField()
    topic = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'
        ordering = ['-created_at']

    def __str__(self):
        return f"Рекомендация для {self.submission.student.username}"

# ----------------- ScheduleEntry -----------------
class ScheduleEntry(models.Model):
    WEEKDAYS = [(0,'Понедельник'),(1,'Вторник'),(2,'Среда'),(3,'Четверг'),(4,'Пятница'),(5,'Суббота')]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedule_entries')
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.CharField(max_length=50, blank=True)
    groups = models.ManyToManyField(Profile, related_name='schedule_entries', blank=True, limit_choices_to={'role':'student'})

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['weekday','start_time']

    def __str__(self):
        return f"{self.course.name} - {self.get_weekday_display()} {self.start_time}"

# ----------------- Student -----------------
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

# ----------------- Enrollment -----------------
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

# ----------------- Lecture -----------------
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

# ----------------- Attendance -----------------
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

# ----------------- Grade -----------------
class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.SET_NULL, null=True, blank=True, related_name='grades')
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True, blank=True, related_name='grades')
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

# ----------------- SmartLearningProfile -----------------
class SmartLearningProfile(models.Model):
    """Умный профиль обучения студента с ИИ-анализом"""
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_profile')
    
    # Стиль обучения (определяется ИИ на основе поведения)
    learning_style = models.CharField(
        max_length=20,
        choices=[
            ('visual', 'Визуальный'),
            ('auditory', 'Аудиальный'),
            ('kinesthetic', 'Кинестетический'),
            ('reading', 'Чтение/Письмо'),
            ('mixed', 'Смешанный')
        ],
        default='mixed',
        verbose_name='Стиль обучения'
    )
    
    # Предпочтения в обучении
    preferred_study_time = models.CharField(
        max_length=20,
        choices=[
            ('morning', 'Утро (6-12)'),
            ('afternoon', 'День (12-18)'),
            ('evening', 'Вечер (18-24)'),
            ('night', 'Ночь (0-6)')
        ],
        default='afternoon',
        verbose_name='Предпочтительное время обучения'
    )
    
    # Анализ производительности
    avg_focus_duration = models.IntegerField(default=45, verbose_name='Средняя длительность фокуса (мин)')
    optimal_study_sessions = models.IntegerField(default=3, verbose_name='Оптимальное количество сессий в день')
    
    # ИИ метрики
    learning_velocity = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.0,
        verbose_name='Скорость обучения (множитель)'
    )
    retention_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.7,
        verbose_name='Коэффициент запоминания'
    )
    
    # Данные для анализа
    study_patterns = models.JSONField(default=dict, verbose_name='Паттерны обучения')
    weak_topics = models.JSONField(default=list, verbose_name='Слабые темы')
    strong_topics = models.JSONField(default=list, verbose_name='Сильные темы')
    
    last_analyzed = models.DateTimeField(auto_now=True, verbose_name='Последний анализ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Умный профиль обучения'
        verbose_name_plural = 'Умные профили обучения'

    def __str__(self):
        return f"Профиль обучения: {self.student.username} ({self.learning_style})"

# ----------------- ExamPrediction -----------------
class ExamPrediction(models.Model):
    """Предсказание успеха на экзамене с помощью ML"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_predictions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exam_predictions')
    
    # Предсказания
    predicted_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Предсказанная оценка'
    )
    success_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Вероятность успеха (%)'
    )
    
    # Факторы
    current_avg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Текущий средний балл')
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Посещаемость (%)')
    assignment_completion = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Выполнение заданий (%)')
    
    # Рекомендации
    recommended_study_hours = models.IntegerField(default=20, verbose_name='Рекомендуемые часы подготовки')
    focus_topics = models.JSONField(default=list, verbose_name='Темы для фокуса')
    risk_factors = models.JSONField(default=list, verbose_name='Факторы риска')
    
    # Метаданные
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Уверенность модели (%)'
    )
    exam_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата экзамена')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Предсказание экзамена'
        verbose_name_plural = 'Предсказания экзаменов'
        ordering = ['-created_at']

    def __str__(self):
        return f"Предсказание: {self.student.username} - {self.course.name} ({self.success_probability}%)"

# ----------------- PersonalizedStudyPlan -----------------
class PersonalizedStudyPlan(models.Model):
    """Персонализированный план обучения, созданный ИИ"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='study_plans')
    
    # План
    plan_name = models.CharField(max_length=200, verbose_name='Название плана')
    target_date = models.DateTimeField(verbose_name='Целевая дата')
    total_hours = models.IntegerField(default=0, verbose_name='Всего часов')
    
    # Структура плана
    daily_schedule = models.JSONField(default=list, verbose_name='Ежедневное расписание')
    topics_priority = models.JSONField(default=dict, verbose_name='Приоритеты тем')
    milestones = models.JSONField(default=list, verbose_name='Вехи')
    
    # Статус
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Прогресс (%)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Персонализированный план обучения'
        verbose_name_plural = 'Персонализированные планы обучения'
        ordering = ['-created_at']

    def __str__(self):
        return f"План: {self.student.username} - {self.course.name} ({self.progress}%)"
