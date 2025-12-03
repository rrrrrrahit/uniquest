from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from main.models import (
    Group, Profile, Student, Course, ScheduleEntry, Enrollment,
    Lecture, Assignment, Grade, Attendance, Submission
)
from datetime import time, timedelta
import random


class Command(BaseCommand):
    help = 'Создает тестового студента с группой, курсами и расписанием'

    def handle(self, *args, **options):
        # Создаем или получаем группу
        group, created = Group.objects.get_or_create(
            name='CS-101',
            defaults={'year': timezone.now().year}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создана группа: {group.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Используется существующая группа: {group.name}'))

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
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Используется существующий пользователь: {username}'))

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
        
        self.stdout.write(self.style.SUCCESS(f'Профиль создан/обновлен для {username}'))

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
        
        self.stdout.write(self.style.SUCCESS(f'Студент создан/обновлен: {student}'))

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
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан курс: {course.name}'))

        # Создаем записи на курсы
        for course in courses:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Студент записан на курс: {course.name}'))

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
                self.stdout.write(self.style.SUCCESS(
                    f'Добавлено расписание: {sched_data["course"].name} - {entry.get_weekday_display()} {sched_data["start_time"]}'
                ))

        # Создаем тестовые задания (много для демонстрации ИИ)
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
                    'days_offset': -60 + hw_num * 5,
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
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Создано задание: {assignment.title}'))
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
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Создано задание: {assignment.title}'))
        
        # Создаем оценки для тестового студента (много разнообразных)
        random.seed(42)  # Для воспроизводимости
        
        # Реалистичные паттерны оценок с трендами для каждого курса
        python_grades = [88, 92, 85, 78, 82, 90, 88, 95, 92, 89,  # ДЗ
                        85, 80, 88, 82, 90,  # Контрольные
                        90, 85, 88, 92, 87, 89, 91, 88, 90,  # Лабораторные
                        95, 92, 98]  # Проекты
        
        db_grades = [72, 68, 70, 75, 73, 78, 75, 80, 78, 82,  # ДЗ
                     65, 70, 72, 75, 78,  # Контрольные
                     70, 72, 75, 78, 80, 82, 85, 83, 88,  # Лабораторные
                     85, 88, 90]  # Проекты
        
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
            grade_value = max(50, min(100, grade_value))
            
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
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана оценка: {grade_value} по {course.name}'))
            assignment_idx += 1
        
        # Создаем дополнительные оценки без заданий (промежуточные тесты, активности)
        additional_topics = {
            courses[0].id: ['Основы Python', 'Переменные', 'Циклы', 'Функции', 'ООП', 'Модули', 'Обработка исключений'],
            courses[1].id: ['SQL основы', 'SELECT', 'JOIN', 'Нормализация', 'Индексы', 'Транзакции', 'Оптимизация'],
            courses[2].id: ['HTML', 'CSS', 'JavaScript', 'DOM', 'AJAX', 'JSON', 'Асинхронность'],
        }
        
        additional_grades_data = {
            courses[0].id: [88, 85, 90, 87, 92, 89, 91],
            courses[1].id: [72, 68, 70, 75, 73, 78, 80],
            courses[2].id: [95, 92, 97, 94, 96, 93, 98],
        }
        
        for course in courses:
            topics = additional_topics.get(course.id, [])
            grades = additional_grades_data.get(course.id, [75] * len(topics))
            
            for i, (topic, grade_val) in enumerate(zip(topics, grades)):
                days_ago = 70 - i * 5
                grade_date = timezone.now() - timedelta(days=days_ago)
                
                final_grade = grade_val + random.randint(-2, 2)
                final_grade = max(50, min(100, final_grade))
                
                grade, created = Grade.objects.get_or_create(
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
                    lecture, created = Lecture.objects.get_or_create(
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
                
                submission, created = Submission.objects.get_or_create(
                    assignment=assignment,
                    student=user,
                    defaults={
                        'text': text,
                        'submitted_at': submitted_at,
                        'score': score,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Создано выполнение: {assignment.title}'))
        
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
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана лекция: {lecture.title}'))

        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Тестовый студент создан успешно!'))
        self.stdout.write(self.style.SUCCESS(f'Логин: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Пароль: {password}'))
        self.stdout.write(self.style.SUCCESS('='*50))

