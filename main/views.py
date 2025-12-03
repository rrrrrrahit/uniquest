from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from functools import wraps
from datetime import timedelta
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

def create_test_student_view(request):
    """Простая страница для создания тестового студента (доступна без авторизации для удобства)"""
    from django.contrib.auth.models import User
    
    # Также создаем администратора, если его нет
    admin_user, admin_created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@uniquest.kz',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if admin_created:
        admin_user.set_password('admin123456')
        admin_user.save()
    
    if request.method == 'POST':
        try:
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
            
            # Создаем тестовые задания (много для демонстрации ИИ)
            from .models import Lecture, Assignment, Submission
            assignments_data = []
            
            # Разные темы для каждого курса
            course_topics_map = {
                courses[0].id: ['Основы Python', 'Переменные и типы', 'Условия и циклы', 'Функции', 'Списки и словари', 'ООП', 'Модули', 'Обработка ошибок', 'Файлы', 'Регулярные выражения'],
                courses[1].id: ['SQL основы', 'SELECT запросы', 'JOIN операции', 'Агрегатные функции', 'Подзапросы', 'Нормализация БД', 'Индексы', 'Транзакции', 'Триггеры', 'Оптимизация'],
                courses[2].id: ['HTML структура', 'CSS стилизация', 'JavaScript основы', 'DOM манипуляции', 'События', 'AJAX', 'JSON', 'LocalStorage', 'Асинхронность', 'Фреймворки'],
            }
            
            for i, course in enumerate(courses):
                topics = course_topics_map.get(course.id, ['Тема 1', 'Тема 2', 'Тема 3'])
                
                # Создаем много заданий разных типов
                course_assignments = []
                
                # Домашние задания (10 штук)
                for hw_num in range(1, 11):
                    topic_idx = (hw_num - 1) % len(topics)
                    course_assignments.append({
                        'title': f'Домашнее задание {hw_num} - {topics[topic_idx]}',
                        'assignment_type': 'homework',
                        'topic': topics[topic_idx],
                        'max_score': 100,
                        'days_offset': -60 + hw_num * 5,  # Распределяем за 60 дней
                    })
                
                # Контрольные работы (5 штук)
                for quiz_num in range(1, 6):
                    topic_idx = (quiz_num * 2 - 1) % len(topics)
                    course_assignments.append({
                        'title': f'Контрольная работа {quiz_num} - {topics[topic_idx]}',
                        'assignment_type': 'quiz',
                        'topic': topics[topic_idx],
                        'max_score': 100,
                        'days_offset': -50 + quiz_num * 8,
                    })
                
                # Лабораторные работы (8 штук)
                for lab_num in range(1, 9):
                    topic_idx = (lab_num * 3 - 2) % len(topics)
                    course_assignments.append({
                        'title': f'Лабораторная работа {lab_num} - {topics[topic_idx]}',
                        'assignment_type': 'lab',
                        'topic': topics[topic_idx],
                        'max_score': 100,
                        'days_offset': -45 + lab_num * 5,
                    })
                
                # Проекты (3 штуки)
                for proj_num in range(1, 4):
                    course_assignments.append({
                        'title': f'Проект {proj_num} - {course.name}',
                        'assignment_type': 'project',
                        'topic': 'Проектирование',
                        'max_score': 100,
                        'days_offset': -30 + proj_num * 10,
                    })
                
                # Итого: 26 заданий на курс
                for ass_data in course_assignments:
                    due_date = timezone.now() + timedelta(days=ass_data['days_offset'])
                    assignment, created = Assignment.objects.get_or_create(
                        course=course,
                        title=ass_data['title'],
                        defaults={
                            'description': f'Подробное описание задания: {ass_data["title"]}. Это задание проверяет понимание темы "{ass_data["topic"]}".',
                            'due_date': due_date,
                            'assignment_type': ass_data['assignment_type'],
                            'topic': ass_data['topic'],
                            'max_score': ass_data['max_score'],
                        }
                    )
                    assignments_data.append((assignment, course))
                for ass_data in course_assignments:
                    due_date = timezone.now() + timedelta(days=ass_data['days_offset'])
                    assignment, created = Assignment.objects.get_or_create(
                        course=course,
                        title=ass_data['title'],
                        defaults={
                            'description': f'Описание задания: {ass_data["title"]}',
                            'due_date': due_date,
                            'assignment_type': ass_data['assignment_type'],
                            'topic': ass_data['topic'],
                            'max_score': ass_data['max_score'],
                        }
                    )
                    assignments_data.append((assignment, course))
            
            # Создаем оценки для тестового студента (много разнообразных для демонстрации ИИ)
            from .models import Grade
            import random
            random.seed(42)  # Для воспроизводимости
            
            # Реалистичные паттерны оценок с трендами для каждого курса
            # Введение в программирование: начинаем хорошо, потом падение, затем восстановление
            python_grades = [88, 92, 85, 78, 82, 90, 88, 95, 92, 89,  # ДЗ
                            85, 80, 88, 82, 90,  # Контрольные
                            90, 85, 88, 92, 87, 89, 91, 88, 90,  # Лабораторные
                            95, 92, 98]  # Проекты
            
            # Базы данных: средние оценки с постепенным улучшением
            db_grades = [72, 68, 70, 75, 73, 78, 75, 80, 78, 82,  # ДЗ
                         65, 70, 72, 75, 78,  # Контрольные
                         70, 72, 75, 78, 80, 82, 85, 83, 88,  # Лабораторные
                         85, 88, 90]  # Проекты
            
            # Веб-разработка: отличные оценки с небольшими колебаниями
            web_grades = [93, 95, 90, 92, 94, 96, 93, 97, 95, 94,  # ДЗ
                          90, 92, 95, 93, 96,  # Контрольные
                          94, 96, 93, 95, 97, 94, 96, 98, 95,  # Лабораторные
                          98, 97, 99]  # Проекты
            
            grade_patterns = {
                courses[0].id: python_grades,
                courses[1].id: db_grades,
                courses[2].id: web_grades,
            }
            
            # Создаем оценки для всех заданий
            assignment_idx = 0
            for assignment, course in assignments_data:
                course_grades = grade_patterns.get(course.id, [75] * 26)
                
                # Берем оценку из паттерна (циклически)
                grade_value = course_grades[assignment_idx % len(course_grades)]
                
                # Добавляем реалистичную вариацию
                variation = random.randint(-2, 2)
                grade_value += variation
                grade_value = max(50, min(100, grade_value))  # Ограничиваем 50-100
                
                # Дата оценки (1-5 дней после дедлайна)
                grade_date = assignment.due_date + timedelta(days=random.randint(1, 5))
                
                # Комментарии в зависимости от оценки
                if grade_value >= 90:
                    comment = f'Отличная работа! Продолжайте в том же духе.'
                elif grade_value >= 80:
                    comment = f'Хорошая работа. Есть небольшие замечания.'
                elif grade_value >= 70:
                    comment = f'Удовлетворительно. Рекомендуется повторить материал.'
                else:
                    comment = f'Требуется дополнительная подготовка по теме "{assignment.topic}".'
                
                # Создаем оценку
                grade, created = Grade.objects.get_or_create(
                    student=user,
                    course=course,
                    assignment=assignment,
                    defaults={
                        'value': grade_value,
                        'topic': assignment.topic,
                        'date': grade_date,
                        'assignment_name': assignment.title,
                        'comment': comment,
                    }
                )
                assignment_idx += 1
            
            # Создаем дополнительные оценки без заданий (промежуточные тесты, активности)
            additional_topics = {
                courses[0].id: ['Основы Python', 'Переменные', 'Циклы', 'Функции', 'ООП', 'Модули', 'Обработка исключений'],
                courses[1].id: ['SQL основы', 'SELECT', 'JOIN', 'Нормализация', 'Индексы', 'Транзакции', 'Оптимизация'],
                courses[2].id: ['HTML', 'CSS', 'JavaScript', 'DOM', 'AJAX', 'JSON', 'Асинхронность'],
            }
            
            additional_grades_data = {
                courses[0].id: [88, 85, 90, 87, 92, 89, 91],  # Python - хорошие оценки
                courses[1].id: [72, 68, 70, 75, 73, 78, 80],  # БД - средние, улучшаются
                courses[2].id: [95, 92, 97, 94, 96, 93, 98],  # Веб - отличные
            }
            
            for course in courses:
                topics = additional_topics.get(course.id, [])
                grades = additional_grades_data.get(course.id, [75] * len(topics))
                
                for i, (topic, grade_val) in enumerate(zip(topics, grades)):
                    days_ago = 70 - i * 5  # Распределяем за последние 70 дней
                    grade_date = timezone.now() - timedelta(days=days_ago)
                    
                    # Добавляем вариацию
                    final_grade = grade_val + random.randint(-2, 2)
                    final_grade = max(50, min(100, final_grade))
                    
                    Grade.objects.get_or_create(
                        student=user,
                        course=course,
                        topic=topic,
                        assignment_name=f'Промежуточный тест: {topic}',
                        defaults={
                            'value': final_grade,
                            'date': grade_date,
                            'comment': f'Проверка знаний по теме "{topic}"',
                        }
                    )
            
            # Создаем посещаемость (реалистичная для демонстрации ИИ)
            from .models import Attendance
            enrollments = Enrollment.objects.filter(student=student)
            
            # Разная посещаемость для разных курсов
            attendance_rates = {
                courses[0].id: 0.92,  # Python - отличная посещаемость
                courses[1].id: 0.78,  # БД - средняя посещаемость
                courses[2].id: 0.95,  # Веб - почти идеальная
            }
            
            # Создаем посещаемость за последние 3 месяца (12 недель)
            for enrollment in enrollments:
                course = enrollment.course
                course_lectures = Lecture.objects.filter(course=course)
                
                # Если лекций еще нет, создадим больше для посещаемости
                if not course_lectures.exists():
                    for i in range(15):  # 15 лекций на курс
                        Lecture.objects.get_or_create(
                            course=course,
                            title=f'Лекция {i+1} - {course.name}',
                            defaults={
                                'content_text': f'Подробное содержание лекции {i+1} по курсу {course.name}. Здесь рассматриваются основные концепции и практические примеры.',
                            }
                        )
                    course_lectures = Lecture.objects.filter(course=course)
                
                attendance_rate = attendance_rates.get(course.id, 0.85)
                
                # Создаем посещаемость за 12 недель
                for lecture in course_lectures[:15]:  # Берем 15 лекций
                    for week in range(12):  # 12 недель назад
                        # Лекции обычно 2 раза в неделю
                        for day_in_week in [0, 3]:  # Понедельник и четверг
                            attendance_date = timezone.now().date() - timedelta(
                                days=week * 7 + day_in_week + random.randint(0, 1)
                            )
                            
                            # Проверяем, не слишком ли старая дата
                            if attendance_date > (timezone.now().date() - timedelta(days=90)):
                                present = random.random() > (1 - attendance_rate)
                                
                                Attendance.objects.get_or_create(
                                    enrollment=enrollment,
                                    lecture=lecture,
                                    date=attendance_date,
                                    defaults={'present': present}
                                )
            
            # Создаем выполнения заданий (submissions) - большинство заданий выполнено
            for assignment, course in assignments_data:
                # 90% заданий выполнено (реалистично)
                if random.random() < 0.90:
                    # Дата сдачи (от 0 до 3 дней до дедлайна - студент сдает вовремя)
                    days_before = random.randint(0, 3)
                    submitted_at = assignment.due_date - timedelta(days=days_before)
                    
                    # Получаем оценку, если есть
                    grade = Grade.objects.filter(student=user, assignment=assignment).first()
                    score = grade.value if grade else None
                    
                    # Текст выполнения зависит от типа задания
                    if assignment.assignment_type == 'homework':
                        text = f'Решение домашнего задания по теме "{assignment.topic}". Выполнены все требования.'
                    elif assignment.assignment_type == 'quiz':
                        text = f'Ответы на контрольную работу по теме "{assignment.topic}".'
                    elif assignment.assignment_type == 'lab':
                        text = f'Отчет по лабораторной работе "{assignment.topic}". Включены код, результаты и выводы.'
                    elif assignment.assignment_type == 'project':
                        text = f'Проект по курсу {course.name}. Включает документацию, код и презентацию.'
                    else:
                        text = f'Выполнение задания: {assignment.title}'
                    
                    Submission.objects.get_or_create(
                        assignment=assignment,
                        student=user,
                        defaults={
                            'text': text,
                            'submitted_at': submitted_at,
                            'score': score,
                        }
                    )
            
            # Создаем тестовые лекции с контентом
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
            
            for lecture_data in lectures_data:
                lecture, created = Lecture.objects.get_or_create(
                    course=lecture_data['course'],
                    title=lecture_data['title'],
                    defaults={
                        'content_text': lecture_data['content_text'],
                    }
                )
            
            return render(request, 'main/create_test_student_success.html', {
                'username': username,
                'password': password,
            })
        except Exception as e:
            return render(request, 'main/create_test_student_error.html', {
                'error': str(e),
            })
    
    return render(request, 'main/create_test_student.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
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
                    # Генерируем уникальный email если он уже существует
                    student_email = user.email or f"{user.username}@example.com"
                    email_base = student_email.split('@')[0]
                    email_domain = student_email.split('@')[1] if '@' in student_email else 'example.com'
                    counter = 1
                    while Student.objects.filter(email=student_email).exists():
                        student_email = f"{email_base}{counter}@{email_domain}"
                        counter += 1
                    
                    Student.objects.get_or_create(
                        user=user,
                        defaults={
                            "first_name": user.first_name or user.username,
                            "last_name": user.last_name or "",
                            "email": student_email,
                            "group": form.cleaned_data.get('group'),
                        },
                    )
                login(request, user)
                messages.success(request, 'Регистрация успешна. Добро пожаловать!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Ошибка при регистрации: {str(e)}')
                # Логируем ошибку для отладки
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Registration error: {str(e)}', exc_info=True)
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
    
    # Проверяем роль преподавателя ПЕРВЫМ делом
    if hasattr(user, 'profile') and user.profile.role == Profile.ROLE_TEACHER:
        return redirect('teacher_dashboard')
    
    # Стандартные роли - только для администраторов
    if user.is_staff:
        # Возможные действия администратора
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

        # Админский дашборд с общей статистикой
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

    # Для студентов (личный кабинет)
    # Получаем курсы, на которые записан студент
    student_profile = getattr(user, 'profile', None)
    if student_profile and student_profile.role == Profile.ROLE_STUDENT:
        # Получаем студента из модели Student
        try:
            student_obj = Student.objects.get(user=user)
            enrollments = Enrollment.objects.filter(student=student_obj).select_related('course')
            courses = [enrollment.course for enrollment in enrollments]
        except Student.DoesNotExist:
            courses = Course.objects.all()[:10]  # Fallback
    else:
        courses = Course.objects.all()[:10]
    
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

@login_required
@student_required
def ai_assistant(request):
    """ИИ-помощник для студентов с поиском по специальности"""
    try:
        user = request.user
        profile = getattr(user, 'profile', None)
        specialty = profile.specialty if profile and hasattr(profile, 'specialty') and profile.specialty else None
        
        # Получаем курсы студента
        student_obj = None
        student_courses = []
        if profile:
            try:
                student_obj = Student.objects.get(user=user)
                enrollments = Enrollment.objects.filter(student=student_obj).select_related('course')
                student_courses = [e.course for e in enrollments if e.course]
            except Student.DoesNotExist:
                pass
            except Exception:
                pass
        
        # Поиск
        query = request.GET.get('q', '').strip()
        search_results = []
        suggested_questions = []
        
        if query:
            try:
                # Семантический поиск по всем лекциям
                all_results = semantic_search(query, top_k=10)
                
                # Загружаем объекты лекций для результатов
                from .models import Lecture
                for result in all_results:
                    lecture_id = result.get('id')
                    if lecture_id:
                        try:
                            lecture = Lecture.objects.select_related('course').get(id=lecture_id)
                            result['lecture'] = lecture
                        except Lecture.DoesNotExist:
                            pass
                        except Exception:
                            pass
                
                # Фильтруем по курсам студента, если есть
                if student_courses:
                    course_ids = [c.id for c in student_courses if c and hasattr(c, 'id')]
                    filtered_results = []
                    other_results = []
                    
                    for result in all_results:
                        lecture = result.get('lecture')
                        if lecture and hasattr(lecture, 'course') and lecture.course:
                            try:
                                if lecture.course.id in course_ids:
                                    filtered_results.append(result)
                                else:
                                    other_results.append(result)
                            except (AttributeError, TypeError):
                                other_results.append(result)
                        else:
                            other_results.append(result)
                    
                    # Сначала показываем результаты из курсов студента
                    search_results = filtered_results + other_results[:5]
                else:
                    search_results = all_results[:10]
            except Exception as e:
                # Если поиск не работает, показываем пустые результаты
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'AI Assistant search error: {str(e)}', exc_info=True)
                search_results = []
                messages.warning(request, 'Поиск временно недоступен. Попробуйте позже.')
        else:
            # Предлагаем вопросы по специальности
            if specialty and hasattr(specialty, 'name_ru'):
                suggested_questions = [
                    f"Что изучают на специальности {specialty.name_ru}?",
                    f"Какие предметы входят в программу {specialty.name_ru}?",
                    f"Основные темы специальности {specialty.name_ru}",
                ]
            else:
                suggested_questions = [
                    "Что такое программирование?",
                    "Основы баз данных",
                    "Веб-разработка для начинающих",
                    "Алгоритмы и структуры данных",
                ]
        
        # Популярные вопросы по специальности
        popular_questions = []
        if specialty and hasattr(specialty, 'name_ru'):
            popular_questions = [
                {"text": f"Какие навыки нужны для {specialty.name_ru}?", "icon": "fa-lightbulb"},
                {"text": f"Карьерные возможности в {specialty.name_ru}", "icon": "fa-briefcase"},
                {"text": f"Сложные темы в {specialty.name_ru}", "icon": "fa-graduation-cap"},
            ]
        
        return render(request, 'main/ai_assistant.html', {
            'query': query,
            'search_results': search_results,
            'suggested_questions': suggested_questions,
            'popular_questions': popular_questions,
            'specialty': specialty,
            'student_courses': student_courses,
        })
    except Exception as e:
        # Общая обработка ошибок
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'AI Assistant error: {str(e)}', exc_info=True)
        messages.error(request, f'Произошла ошибка: {str(e)}')
        return render(request, 'main/ai_assistant.html', {
            'query': request.GET.get('q', '').strip(),
            'search_results': [],
            'suggested_questions': [
                "Что такое программирование?",
                "Основы баз данных",
                "Веб-разработка для начинающих",
            ],
            'popular_questions': [],
            'specialty': None,
            'student_courses': [],
        })


@login_required
@student_required
def ai_learning_assistant(request):
    """Революционный ИИ-ассистент для персонализированного обучения"""
    from .ai_learning_service import (
        analyze_learning_style, get_ai_recommendations,
        predict_exam_success, create_personalized_study_plan
    )
    from .models import ExamPrediction, PersonalizedStudyPlan
    
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Получаем курсы студента
    student_obj = None
    student_courses = []
    if profile:
        try:
            student_obj = Student.objects.get(user=user)
            enrollments = Enrollment.objects.filter(student=student_obj).select_related('course')
            student_courses = [e.course for e in enrollments if e.course]
        except Student.DoesNotExist:
            pass
    
    # Анализируем стиль обучения
    learning_profile = None
    try:
        learning_profile = analyze_learning_style(user)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error analyzing learning style: {str(e)}')
    
    # Получаем рекомендации для всех курсов
    all_recommendations = {}
    exam_predictions = {}
    study_plans = {}
    
    for course in student_courses:
        try:
            recommendations = get_ai_recommendations(user, course)
            all_recommendations[course.id] = recommendations
            
            # Получаем последнее предсказание
            prediction = ExamPrediction.objects.filter(
                student=user, course=course
            ).order_by('-created_at').first()
            if prediction:
                exam_predictions[course.id] = prediction
            
            # Получаем активный план
            plan = PersonalizedStudyPlan.objects.filter(
                student=user, course=course, is_active=True
            ).order_by('-created_at').first()
            if plan:
                study_plans[course.id] = plan
        except Exception:
            pass
    
    return render(request, 'main/ai_learning_assistant.html', {
        'learning_profile': learning_profile,
        'student_courses': student_courses,
        'recommendations': all_recommendations,
        'exam_predictions': exam_predictions,
        'study_plans': study_plans,
    })


@login_required
@student_required
def predict_exam_view(request, course_id):
    """Предсказание успеха на экзамене"""
    from .ai_learning_service import predict_exam_success
    from .models import Course
    
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        exam_date_str = request.POST.get('exam_date')
        exam_date = None
        if exam_date_str:
            try:
                from datetime import datetime
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
                exam_date = timezone.make_aware(exam_date)
            except Exception:
                pass
        
        try:
            prediction = predict_exam_success(request.user, course, exam_date)
            messages.success(request, 'Предсказание успешно создано!')
            return redirect('ai_learning_assistant')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
    
    return redirect('ai_learning_assistant')


@login_required
@student_required
def create_study_plan_view(request, course_id):
    """Создание персонализированного плана обучения"""
    from .ai_learning_service import create_personalized_study_plan
    from .models import Course
    
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        target_date_str = request.POST.get('target_date')
        if not target_date_str:
            messages.error(request, 'Укажите целевую дату')
            return redirect('ai_learning_assistant')
        
        try:
            from datetime import datetime
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
            target_date = timezone.make_aware(target_date)
            
            if target_date <= timezone.now():
                messages.error(request, 'Целевая дата должна быть в будущем')
                return redirect('ai_learning_assistant')
            
            plan = create_personalized_study_plan(request.user, course, target_date)
            messages.success(request, f'Персонализированный план создан! Всего часов: {plan.total_hours}')
            return redirect('ai_learning_assistant')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
    
    return redirect('ai_learning_assistant')


# ===== Публичные академические страницы =====

def groups_list(request):
    """Список всех групп"""
    groups = Group.objects.all().order_by('-year', 'name')
    # Добавляем количество студентов в каждой группе
    for group in groups:
        group.student_count = Profile.objects.filter(group=group, role=Profile.ROLE_STUDENT).count()
    return render(request, 'main/groups_list.html', {'groups': groups})

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
