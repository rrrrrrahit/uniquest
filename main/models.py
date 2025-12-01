from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

# Специальности для Казахстана
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

# Предметы/Дисциплины
class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Код предмета')
    name_kk = models.CharField(max_length=200, verbose_name='Название (каз)')
    name_ru = models.CharField(max_length=200, verbose_name='Название (рус)')
    credits = models.IntegerField(default=3, verbose_name='Кредиты')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='subjects', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name_ru}"

class Profile(models.Model):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Студент'),
        (ROLE_TEACHER, 'Преподаватель'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    group = models.CharField(max_length=50, blank=True, verbose_name='Группа')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='Специальность')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name='Биография')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    iin = models.CharField(max_length=12, blank=True, verbose_name='ИИН')
    address = models.TextField(blank=True, verbose_name='Адрес')
    enrollment_date = models.DateField(null=True, blank=True, verbose_name='Дата поступления')
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    code = models.CharField(max_length=20, blank=True, verbose_name='Код курса')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name='Предмет')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_courses', verbose_name='Преподаватель')
    description = models.TextField(blank=True, verbose_name='Описание')
    credits = models.IntegerField(default=3, verbose_name='Кредиты')
    semester = models.IntegerField(choices=[(1, 'Осенний'), (2, 'Весенний')], default=1, verbose_name='Семестр')
    academic_year = models.CharField(max_length=9, default='2024-2025', verbose_name='Учебный год')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-academic_year', 'semester', 'code']
    
    def __str__(self):
        return f"{self.code or ''} {self.name}".strip()

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', verbose_name='Курс')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    due_date = models.DateTimeField(verbose_name='Срок сдачи')
    max_score = models.IntegerField(default=100, verbose_name='Максимальный балл')
    topic = models.CharField(max_length=200, blank=True, verbose_name='Тема')
    assignment_type = models.CharField(max_length=50, choices=[
        ('homework', 'Домашнее задание'),
        ('project', 'Проект'),
        ('quiz', 'Контрольная работа'),
        ('exam', 'Экзамен'),
        ('lab', 'Лабораторная работа'),
    ], default='homework', verbose_name='Тип задания')
    
    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions', verbose_name='Задание')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', verbose_name='Студент')
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    text = models.TextField(blank=True, verbose_name='Текст работы')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата сдачи')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Оценка')
    
    class Meta:
        verbose_name = 'Работа студента'
        verbose_name_plural = 'Работы студентов'
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

# Прогноз проблем с использованием ИИ/ML
class ProblemPrediction(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='prediction', verbose_name='Работа')
    predicted_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Прогнозируемый балл')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('low', 'Низкая'),
        ('medium', 'Средняя'),
        ('high', 'Высокая'),
    ], blank=True, verbose_name='Уровень сложности')
    problem_areas = models.JSONField(default=list, verbose_name='Проблемные области')
    recommendations = models.TextField(blank=True, verbose_name='Рекомендации')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Уверенность (%)')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Прогноз проблем'
        verbose_name_plural = 'Прогнозы проблем'
    
    def __str__(self):
        return f"Прогноз для {self.submission.student.username}"

class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records', verbose_name='Студент')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress', verbose_name='Курс')
    topic = models.CharField(max_length=200, verbose_name='Тема')
    understanding_level = models.IntegerField(choices=[(1, 'Плохо'), (2, 'Удовлетворительно'), (3, 'Хорошо'), (4, 'Отлично')], verbose_name='Уровень понимания')
    issues = models.JSONField(default=list, verbose_name='Проблемы')
    recommendations = models.TextField(blank=True, verbose_name='Рекомендации')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Прогресс студента'
        verbose_name_plural = 'Прогресс студентов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.name} - {self.topic}"

class Recommendation(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='recommendations', verbose_name='Работа')
    text = models.TextField(verbose_name='Рекомендация')
    topic = models.CharField(max_length=200, blank=True, verbose_name='Тема')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Рекомендация для {self.submission.student.username}"

class ScheduleEntry(models.Model):
    WEEKDAYS = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedule_entries', verbose_name='Курс')
    weekday = models.IntegerField(choices=WEEKDAYS, verbose_name='День недели')
    start_time = models.TimeField(verbose_name='Время начала')
    end_time = models.TimeField(verbose_name='Время окончания')
    classroom = models.CharField(max_length=50, blank=True, verbose_name='Аудитория')
    groups = models.ManyToManyField('Profile', related_name='schedule_entries', blank=True, limit_choices_to={'role': 'student'}, verbose_name='Группы')
    
    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['weekday', 'start_time']
    
    def __str__(self):
        return f"{self.course.name} - {self.get_weekday_display()} {self.start_time}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades', verbose_name='Студент')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades', verbose_name='Курс')
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True, blank=True, related_name='grades', verbose_name='Задание')
    value = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Балл')
    letter_grade = models.CharField(max_length=5, choices=[
        ('A', 'A (отлично)'),
        ('B', 'B (хорошо)'),
        ('C', 'C (удовлетворительно)'),
        ('D', 'D (плохо)'),
        ('F', 'F (неудовлетворительно)'),
    ], blank=True, verbose_name='Буквенная оценка')
    date = models.DateTimeField(default=timezone.now, verbose_name='Дата')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    topic = models.CharField(max_length=200, blank=True, verbose_name='Тема')
    
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        ordering = ['-date']
    
    def save(self, *args, **kwargs):
        # Автоматическое определение буквенной оценки
        if not self.letter_grade and self.value:
            if self.value >= 90:
                self.letter_grade = 'A'
            elif self.value >= 80:
                self.letter_grade = 'B'
            elif self.value >= 70:
                self.letter_grade = 'C'
            elif self.value >= 60:
                self.letter_grade = 'D'
            else:
                self.letter_grade = 'F'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.username} - {self.course.name} - {self.value}"
