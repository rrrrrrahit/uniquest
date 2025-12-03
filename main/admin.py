from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Specialty, Subject, Group, Profile, Course, Assignment, Submission,
    ProblemPrediction, StudentProgress, Recommendation, ScheduleEntry,
    Grade, Student, Enrollment, Lecture, Attendance
)

# ----------------- Specialty -----------------
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_ru', 'name_kk')
    search_fields = ('code', 'name_ru', 'name_kk')
    ordering = ('code',)

# ----------------- Subject -----------------
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_ru', 'name_kk', 'credits', 'specialty')
    list_filter = ('specialty',)
    search_fields = ('code', 'name_ru', 'name_kk')
    ordering = ('code',)

# ----------------- Group -----------------
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'created_at')
    search_fields = ('name',)
    ordering = ('-year', 'name')

# ----------------- Profile -----------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'group', 'specialty')
    list_filter = ('role', 'group', 'specialty')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('user__username',)

# ----------------- Course -----------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'teacher', 'credits', 'semester', 'academic_year')
    list_filter = ('semester', 'academic_year', 'subject')
    search_fields = ('name', 'code')
    ordering = ('-academic_year', 'semester', 'code')

# ----------------- Assignment -----------------
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assignment_type', 'due_date', 'max_score')
    list_filter = ('assignment_type', 'course')
    search_fields = ('title', 'course__name')
    ordering = ('-due_date',)

# ----------------- Submission -----------------
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'score')
    list_filter = ('assignment__course', 'submitted_at')
    search_fields = ('student__username', 'assignment__title')
    ordering = ('-submitted_at',)

# ----------------- ProblemPrediction -----------------
@admin.register(ProblemPrediction)
class ProblemPredictionAdmin(admin.ModelAdmin):
    list_display = ('submission', 'difficulty_level', 'predicted_score', 'confidence')
    list_filter = ('difficulty_level',)
    ordering = ('-confidence',)

# ----------------- StudentProgress -----------------
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'topic', 'understanding_level', 'created_at')
    list_filter = ('understanding_level', 'course')
    search_fields = ('student__username', 'topic')
    ordering = ('-created_at',)

# ----------------- Recommendation -----------------
@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('submission', 'topic', 'created_at')
    search_fields = ('topic', 'text')
    ordering = ('-created_at',)

# ----------------- ScheduleEntry -----------------
@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('course', 'weekday', 'start_time', 'end_time', 'classroom')
    list_filter = ('weekday', 'course')
    search_fields = ('course__name', 'classroom')
    ordering = ('weekday', 'start_time')

# ----------------- Student -----------------
def create_test_student_action(modeladmin, request, queryset):
    """Admin action для создания тестового студента"""
    try:
        from datetime import time
        
        # Создаем или получаем группу
        group, created = Group.objects.get_or_create(
            name='CS-101',
            defaults={'year': timezone.now().year}
        )
        
        # Создаем или получаем пользователя
        username = 'test_student'
        password = 'test123456'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'test_student@example.com',
                'first_name': 'Тестовый',
                'last_name': 'Студент',
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
        
        # Создаем или обновляем профиль
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'role': Profile.ROLE_STUDENT,
                'group': group,
            }
        )
        if not created:
            profile.group = group
            profile.role = Profile.ROLE_STUDENT
            profile.save()
        
        # Создаем или получаем студента
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'group': group,
            }
        )
        if not created:
            student.group = group
            student.save()
        
        # Создаем тестовые курсы
        courses_data = [
            {'name': 'Введение в программирование', 'code': 'CS101'},
            {'name': 'Базы данных', 'code': 'CS102'},
            {'name': 'Веб-разработка', 'code': 'CS201'},
        ]
        
        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'name': course_data['name'],
                    'description': f'Описание курса {course_data["name"]}',
                    'credits': 3,
                }
            )
            courses.append(course)
        
        # Создаем записи на курсы
        for course in courses:
            Enrollment.objects.get_or_create(
                student=student,
                course=course,
            )
        
        # Создаем расписание
        schedule_data = [
            {'weekday': 0, 'start_time': '09:00', 'end_time': '10:30', 'course': courses[0]},
            {'weekday': 1, 'start_time': '10:40', 'end_time': '12:10', 'course': courses[1]},
            {'weekday': 2, 'start_time': '13:00', 'end_time': '14:30', 'course': courses[2]},
            {'weekday': 3, 'start_time': '09:00', 'end_time': '10:30', 'course': courses[0]},
            {'weekday': 4, 'start_time': '10:40', 'end_time': '12:10', 'course': courses[1]},
        ]
        
        for sched_data in schedule_data:
            entry, created = ScheduleEntry.objects.get_or_create(
                course=sched_data['course'],
                weekday=sched_data['weekday'],
                start_time=sched_data['start_time'],
                end_time=sched_data['end_time'],
                defaults={'classroom': 'Аудитория 101'}
            )
            if created or not entry.groups.filter(id=profile.id).exists():
                entry.groups.add(profile)
        
        # Создаем тестовые лекции с контентом
        from .models import Lecture
        lectures_data = [
            {
                'course': courses[0],  # Введение в программирование
                'title': 'Введение в Python',
                'content_text': '''Python - это высокоуровневый язык программирования общего назначения. Он был создан Гвидо ван Россумом и впервые выпущен в 1991 году.

Основные особенности Python:
- Простой и читаемый синтаксис
- Динамическая типизация
- Интерпретируемый язык
- Кроссплатформенность
- Большая стандартная библиотека

Python используется для веб-разработки, анализа данных, машинного обучения, автоматизации и многого другого. Это отличный язык для начинающих программистов благодаря своей простоте и понятности.

Пример простой программы на Python:
print("Привет, мир!")
x = 10
y = 20
print(f"Сумма: {x + y}")'''
            },
            {
                'course': courses[0],
                'title': 'Переменные и типы данных',
                'content_text': '''В Python переменные создаются простым присваиванием значения. Не нужно объявлять тип переменной заранее.

Основные типы данных:
- Числа (int, float): 10, 3.14
- Строки (str): "Привет", 'Мир'
- Списки (list): [1, 2, 3]
- Словари (dict): {"ключ": "значение"}
- Булевы значения (bool): True, False

Примеры:
age = 25
name = "Иван"
grades = [5, 4, 5, 3]
student = {"имя": "Иван", "возраст": 25}'''
            },
            {
                'course': courses[0],
                'title': 'Условия и циклы',
                'content_text': '''Условные операторы позволяют выполнять код в зависимости от условий.

if-elif-else:
if x > 0:
    print("Положительное")
elif x < 0:
    print("Отрицательное")
else:
    print("Ноль")

Циклы позволяют повторять код:
for i in range(5):
    print(i)

while x < 10:
    x += 1
    print(x)'''
            },
            {
                'course': courses[1],  # Базы данных
                'title': 'Введение в SQL',
                'content_text': '''SQL (Structured Query Language) - язык для работы с реляционными базами данных.

Основные команды:
- SELECT - выборка данных
- INSERT - вставка данных
- UPDATE - обновление данных
- DELETE - удаление данных
- CREATE TABLE - создание таблицы

Пример SELECT:
SELECT имя, фамилия FROM студенты WHERE группа = 'CS-101';

Пример INSERT:
INSERT INTO студенты (имя, фамилия, группа) 
VALUES ('Иван', 'Иванов', 'CS-101');'''
            },
            {
                'course': courses[1],
                'title': 'Нормализация баз данных',
                'content_text': '''Нормализация - процесс организации данных в базе для уменьшения избыточности.

Основные нормальные формы:
1NF - каждая ячейка содержит одно значение
2NF - 1NF + нет частичных зависимостей
3NF - 2NF + нет транзитивных зависимостей

Преимущества нормализации:
- Уменьшение дублирования данных
- Улучшение целостности данных
- Упрощение обновлений
- Экономия места'''
            },
            {
                'course': courses[1],
                'title': 'JOIN операции',
                'content_text': '''JOIN позволяет объединять данные из нескольких таблиц.

Типы JOIN:
- INNER JOIN - только совпадающие записи
- LEFT JOIN - все записи из левой таблицы
- RIGHT JOIN - все записи из правой таблицы
- FULL OUTER JOIN - все записи из обеих таблиц

Пример:
SELECT студенты.имя, курсы.название
FROM студенты
INNER JOIN записи ON студенты.id = записи.студент_id
INNER JOIN курсы ON записи.курс_id = курсы.id;'''
            },
            {
                'course': courses[2],  # Веб-разработка
                'title': 'HTML основы',
                'content_text': '''HTML (HyperText Markup Language) - язык разметки для создания веб-страниц.

Основные теги:
- <html> - корневой элемент
- <head> - метаинформация
- <body> - содержимое страницы
- <h1>-<h6> - заголовки
- <p> - параграф
- <a> - ссылка
- <img> - изображение
- <div> - контейнер

Пример:
<!DOCTYPE html>
<html>
<head>
    <title>Моя страница</title>
</head>
<body>
    <h1>Привет, мир!</h1>
    <p>Это моя первая веб-страница.</p>
</body>
</html>'''
            },
            {
                'course': courses[2],
                'title': 'CSS стилизация',
                'content_text': '''CSS (Cascading Style Sheets) - язык для стилизации HTML элементов.

Способы подключения CSS:
1. Внутренний стиль: <style>...</style>
2. Внешний файл: <link rel="stylesheet" href="style.css">
3. Инлайн: <div style="color: red;">

Основные свойства:
- color - цвет текста
- background-color - цвет фона
- font-size - размер шрифта
- margin - внешние отступы
- padding - внутренние отступы
- border - граница

Пример:
h1 {
    color: blue;
    font-size: 24px;
    margin: 20px;
}'''
            },
            {
                'course': courses[2],
                'title': 'JavaScript основы',
                'content_text': '''JavaScript - язык программирования для создания интерактивных веб-страниц.

Основные концепции:
- Переменные: let, const, var
- Функции: function, arrow functions
- Объекты и массивы
- DOM манипуляции
- События

Пример:
let name = "Иван";
function greet(name) {
    console.log("Привет, " + name + "!");
}
greet(name);

// Работа с DOM
document.getElementById("myButton").addEventListener("click", function() {
    alert("Кнопка нажата!");
});'''
            },
        ]
        
        lectures_created = 0
        for lecture_data in lectures_data:
            lecture, created = Lecture.objects.get_or_create(
                course=lecture_data['course'],
                title=lecture_data['title'],
                defaults={
                    'content_text': lecture_data['content_text'],
                }
            )
            if created:
                lectures_created += 1
        
        messages.success(request, f'✅ Тестовый студент создан! Логин: {username}, Пароль: {password}. Создано лекций: {lectures_created}')
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')

create_test_student_action.short_description = "Создать тестового студента (test_student / test123456)"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'group', 'is_active', 'created_at')
    list_filter = ('group', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')
    actions = [create_test_student_action]

# ----------------- Enrollment -----------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__first_name', 'student__last_name', 'course__name')
    ordering = ('-enrolled_at',)

# ----------------- Lecture -----------------
@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content_text', 'course__name')
    ordering = ('-created_at',)

# ----------------- Attendance -----------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lecture', 'date', 'present')
    list_filter = ('present', 'date', 'lecture__course')
    search_fields = ('enrollment__student__first_name', 'enrollment__student__last_name')
    ordering = ('-date',)

# ----------------- Grade -----------------
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'value', 'letter_grade', 'date', 'assignment_name')
    list_filter = ('letter_grade', 'course', 'date')
    search_fields = ('student__username', 'course__name', 'assignment_name', 'topic')
    ordering = ('-date',)

