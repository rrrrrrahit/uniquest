"""
Скрипт для генерации большого количества данных для UniQuest
С казахстанским контекстом - студенты, преподаватели, курсы, оценки
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uniquest.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import (
    Profile, Specialty, Subject, Course, Grade, Assignment,
    ScheduleEntry, StudentProgress, ProblemPrediction
)
from django.utils import timezone

# Казахстанские данные
KAZAKHSTAN_CITIES = [
    'Алматы', 'Нур-Султан', 'Шымкент', 'Актобе', 'Караганда',
    'Тараз', 'Павлодар', 'Усть-Каменогорск', 'Семей', 'Атырау',
    'Кызылорда', 'Костанай', 'Петропавловск', 'Уральск', 'Туркестан'
]

KAZAKH_NAMES = [
    ('Айдан', 'Қасымов'), ('Нурлан', 'Ахметов'), ('Данияр', 'Омаров'),
    ('Азамат', 'Ермеков'), ('Ерлан', 'Смагулов'), ('Асылбек', 'Нуртазин'),
    ('Дамир', 'Абдуллаев'), ('Айбек', 'Сапарбеков'), ('Рустем', 'Токтаров'),
    ('Алмаз', 'Калиев'), ('Бахтияр', 'Мамедов'), ('Жанат', 'Ибрагимов'),
    ('Марат', 'Усенов'), ('Тимур', 'Байжанов'), ('Асыл', 'Жумабеков'),
]

RUSSIAN_NAMES = [
    ('Александр', 'Петров'), ('Дмитрий', 'Иванов'), ('Андрей', 'Сидоров'),
    ('Сергей', 'Кузнецов'), ('Алексей', 'Смирнов'), ('Максим', 'Попов'),
    ('Владимир', 'Соколов'), ('Игорь', 'Лебедев'), ('Николай', 'Козлов'),
    ('Роман', 'Новиков'), ('Павел', 'Морозов'), ('Антон', 'Волков'),
]

FEMALE_NAMES = [
    ('Айгуль', 'Касымова'), ('Алина', 'Ахметова'), ('Дана', 'Омарова'),
    ('Асель', 'Ермекова'), ('Гульнара', 'Смагулова'), ('Сабина', 'Нуртазина'),
    ('Амина', 'Абдуллаева'), ('Айша', 'Сапарбекова'), ('Аружан', 'Токтарова'),
    ('Динара', 'Калиева'), ('Малика', 'Мамедова'), ('Жанара', 'Ибрагимова'),
    ('Мария', 'Петрова'), ('Анна', 'Иванова'), ('Елена', 'Сидорова'),
    ('Ольга', 'Кузнецова'), ('Наталья', 'Смирнова'), ('Татьяна', 'Попова'),
]

SPECIALTIES_DATA = [
    ('IT-001', 'Ақпараттық жүйелер', 'Информационные системы'),
    ('IT-002', 'Компьютерлік инженерия', 'Компьютерная инженерия'),
    ('IT-003', 'Бағдарламалық инженерия', 'Программная инженерия'),
    ('EC-001', 'Экономика', 'Экономика'),
    ('EC-002', 'Бизнес-басқару', 'Бизнес-управление'),
    ('EC-003', 'Есеп және аудит', 'Учет и аудит'),
    ('EN-001', 'Ағылшын тілі', 'Английский язык'),
    ('EN-002', 'Тілдерді оқыту', 'Преподавание языков'),
    ('LA-001', 'Құқықтану', 'Юриспруденция'),
    ('LA-002', 'Халықаралық құқық', 'Международное право'),
    ('ME-001', 'Медицина', 'Медицина'),
    ('EN-003', 'Инженерлік', 'Инженерия'),
]

SUBJECTS_DATA = [
    ('ПРОГ', 'Бағдарламалау негіздері', 'Основы программирования'),
    ('ВЕБ', 'Веб-технологиялар', 'Веб-технологии'),
    ('БД', 'Мәліметтер қоры', 'Базы данных'),
    ('АЛГ', 'Алгоритмдер', 'Алгоритмы'),
    ('ИИ', 'Жасанды интеллект', 'Искусственный интеллект'),
    ('БЕЗ', 'Киберқауіпсіздік', 'Кибербезопасность'),
    ('ЭКОН', 'Экономика негіздері', 'Основы экономики'),
    ('МАРК', 'Маркетинг', 'Маркетинг'),
    ('ФИН', 'Қаржы', 'Финансы'),
    ('ПРАВ', 'Құқық негіздері', 'Основы права'),
    ('АНГЛ', 'Ағылшын тілі', 'Английский язык'),
    ('МАТ', 'Математика', 'Математика'),
    ('ФИЗ', 'Физика', 'Физика'),
]

TOPICS = [
    'Введение в предмет', 'Основные концепции', 'Практическое применение',
    'Теоретические основы', 'Анализ данных', 'Практические задания',
    'Промежуточный контроль', 'Итоговое тестирование', 'Самостоятельная работа',
    'Лабораторные работы', 'Проектная деятельность', 'Курсовая работа',
]

GROUPS = [
    'IT-21-01', 'IT-21-02', 'IT-22-01', 'IT-22-02', 'IT-23-01', 'IT-23-02',
    'EC-21-01', 'EC-21-02', 'EC-22-01', 'EC-22-02', 'EC-23-01',
    'EN-21-01', 'EN-22-01', 'LA-21-01', 'LA-22-01',
    'ME-21-01', 'EN-21-02', 'EN-22-02',
]


def create_specialties():
    """Создание специальностей"""
    print("Создание специальностей...")
    specialties = []
    for code, name_kk, name_ru in SPECIALTIES_DATA:
        spec, created = Specialty.objects.get_or_create(
            code=code,
            defaults={
                'name_kk': name_kk,
                'name_ru': name_ru,
                'description': f'Специальность {name_ru} - подготовка специалистов в области {name_ru}'
            }
        )
        specialties.append(spec)
        if created:
            print(f"  ✓ Создана специальность: {code} - {name_ru}")
    return specialties


def create_subjects(specialties):
    """Создание предметов"""
    print("\nСоздание предметов...")
    subjects = []
    for code, name_kk, name_ru in SUBJECTS_DATA:
        # Привязываем предметы к соответствующим специальностям
        specialty = None
        if code.startswith('ПРОГ') or code.startswith('ВЕБ') or code.startswith('БД') or code.startswith('АЛГ') or code.startswith('ИИ') or code.startswith('БЕЗ'):
            specialty = next((s for s in specialties if s.code.startswith('IT')), None)
        elif code.startswith('ЭКОН') or code.startswith('МАРК') or code.startswith('ФИН'):
            specialty = next((s for s in specialties if s.code.startswith('EC')), None)
        
        subj, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                'name_kk': name_kk,
                'name_ru': name_ru,
                'credits': random.choice([2, 3, 4, 5]),
                'specialty': specialty
            }
        )
        subjects.append(subj)
        if created:
            print(f"  ✓ Создан предмет: {code} - {name_ru}")
    return subjects


def create_teachers(count=15):
    """Создание преподавателей"""
    print(f"\nСоздание {count} преподавателей...")
    teachers = []
    all_names = KAZAKH_NAMES + RUSSIAN_NAMES + FEMALE_NAMES
    
    for i in range(count):
        first_name, last_name = random.choice(all_names)
        username = f'teacher_{i+1:03d}'
        email = f'teacher{i+1}@uniquest.kz'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'is_active': True,
            }
        )
        
        if created:
            user.set_password('teacher123')
            user.save()
        
        profile, p_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'role': Profile.ROLE_TEACHER,
                'phone': f'+7{random.randint(7000000000, 7999999999)}',
                'address': f'{random.choice(KAZAKHSTAN_CITIES)}, ул. {random.choice(["Абая", "Сатыбалды", "Достык", "Фурманова"])}',
                'bio': f'Опытный преподаватель в области образования. Стаж работы: {random.randint(5, 25)} лет.',
            }
        )
        
        teachers.append(user)
        if created or p_created:
            print(f"  ✓ Создан преподаватель: {first_name} {last_name} ({username})")
    
    return teachers


def create_students(count=200):
    """Создание студентов"""
    print(f"\nСоздание {count} студентов...")
    students = []
    all_names = KAZAKH_NAMES + RUSSIAN_NAMES + FEMALE_NAMES
    specialties = list(Specialty.objects.all())
    
    for i in range(count):
        first_name, last_name = random.choice(all_names)
        username = f'student_{i+1:04d}'
        email = f'student{i+1}@student.uniquest.kz'
        group = random.choice(GROUPS)
        specialty = random.choice(specialties) if specialties else None
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'is_active': True,
            }
        )
        
        if created:
            user.set_password('student123')
            user.save()
        
        enrollment_date = timezone.now().date() - timedelta(days=random.randint(30, 400))
        
        profile, p_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'role': Profile.ROLE_STUDENT,
                'group': group,
                'specialty': specialty,
                'phone': f'+7{random.randint(7000000000, 7999999999)}',
                'address': f'{random.choice(KAZAKHSTAN_CITIES)}, ул. {random.choice(["Абая", "Сатыбалды", "Достык", "Фурманова"])}',
                'iin': f'{random.randint(900000000000, 999999999999)}',
                'enrollment_date': enrollment_date,
                'bio': f'Студент группы {group}',
            }
        )
        
        students.append(user)
        if created or p_created and i % 20 == 0:
            print(f"  ✓ Создано студентов: {i+1}/{count}")
    
    print(f"  ✓ Всего создано студентов: {len(students)}")
    return students


def create_courses(subjects, teachers):
    """Создание курсов"""
    print(f"\nСоздание курсов...")
    courses = []
    academic_years = ['2023-2024', '2024-2025']
    
    for subject in subjects:
        for year in academic_years:
            for semester in [1, 2]:
                teacher = random.choice(teachers)
                code = f"{subject.code}-{year[:4]}-{semester}"
                
                course, created = Course.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': f"{subject.name_ru} ({year}, семестр {semester})",
                        'subject': subject,
                        'teacher': teacher,
                        'description': f'Курс по предмету {subject.name_ru}. Изучение основных концепций и практическое применение.',
                        'credits': subject.credits,
                        'semester': semester,
                        'academic_year': year,
                        'created_at': timezone.now() - timedelta(days=random.randint(100, 400)),
                    }
                )
                courses.append(course)
                if created:
                    print(f"  ✓ Создан курс: {code} - {course.name}")
    
    return courses


def create_assignments(courses):
    """Создание заданий"""
    print(f"\nСоздание заданий...")
    assignments = []
    assignment_types = ['homework', 'project', 'quiz', 'exam', 'lab']
    
    for course in courses:
        # Создаем несколько заданий на курс
        for i in range(random.randint(3, 8)):
            due_date = timezone.now() + timedelta(days=random.randint(-100, 30))
            if due_date < timezone.now():
                due_date = timezone.now() + timedelta(days=random.randint(1, 30))
            
            assignment, created = Assignment.objects.get_or_create(
                course=course,
                title=f"{random.choice(TOPICS)} - {i+1}",
                defaults={
                    'description': f'Задание по теме "{random.choice(TOPICS)}"',
                    'due_date': due_date,
                    'max_score': random.choice([50, 100]),
                    'topic': random.choice(TOPICS),
                    'assignment_type': random.choice(assignment_types),
                }
            )
            assignments.append(assignment)
    
    print(f"  ✓ Создано заданий: {len(assignments)}")
    return assignments


def create_grades(students, courses):
    """Создание оценок"""
    print(f"\nСоздание оценок...")
    grades_created = 0
    
    for course in courses:
        # Получаем студентов, которые могут быть на этом курсе
        course_students = random.sample(
            list(students), 
            min(random.randint(15, 40), len(students))
        )
        
        for student in course_students:
            # Создаем несколько оценок для каждого студента по курсу
            for _ in range(random.randint(2, 6)):
                grade_date = timezone.now() - timedelta(days=random.randint(1, 200))
                value = Decimal(str(random.uniform(45, 100))).quantize(Decimal('0.01'))
                
                grade, created = Grade.objects.get_or_create(
                    student=student,
                    course=course,
                    topic=random.choice(TOPICS),
                    defaults={
                        'value': value,
                        'date': grade_date,
                        'comment': random.choice([
                            'Хорошая работа', 'Требуется улучшение', 
                            'Отлично выполнено', 'Есть замечания',
                            'Работа выполнена в срок', ''
                        ]),
                    }
                )
                
                if created:
                    grades_created += 1
        
        if grades_created % 100 == 0:
            print(f"  ✓ Создано оценок: {grades_created}")
    
    print(f"  ✓ Всего создано оценок: {grades_created}")
    return grades_created


def create_schedule(courses):
    """Создание расписания"""
    print(f"\nСоздание расписания...")
    schedule_entries = []
    weekdays = [0, 1, 2, 3, 4]  # Понедельник - Пятница
    times = [
        ('09:00', '10:30'), ('10:40', '12:10'), ('12:30', '14:00'),
        ('14:10', '15:40'), ('15:50', '17:20'), ('17:30', '19:00')
    ]
    
    for course in courses[:len(courses)//2]:  # Расписание только для половины курсов
        weekday = random.choice(weekdays)
        start_time, end_time = random.choice(times)
        
        schedule_entry = ScheduleEntry.objects.create(
            course=course,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            classroom=f"{random.randint(100, 500)}-{random.choice(['А', 'Б', 'В'])}",
        )
        
        # Добавляем случайные группы
        student_profiles = list(Profile.objects.filter(role='student', group__isnull=False).distinct('group')[:3])
        schedule_entry.groups.set(random.sample(student_profiles, min(2, len(student_profiles))))
        
        schedule_entries.append(schedule_entry)
    
    print(f"  ✓ Создано записей расписания: {len(schedule_entries)}")
    return schedule_entries


def create_progress_records(students, courses):
    """Создание записей о прогрессе студентов"""
    print(f"\nСоздание записей о прогрессе...")
    progress_count = 0
    
    for course in courses[:20]:  # Для части курсов
        course_students = random.sample(
            list(students),
            min(10, len(students))
        )
        
        for student in course_students:
            if random.random() < 0.3:  # 30% студентов имеют записи о прогрессе
                progress, created = StudentProgress.objects.get_or_create(
                    student=student,
                    course=course,
                    topic=random.choice(TOPICS),
                    defaults={
                        'understanding_level': random.randint(1, 4),
                        'issues': random.sample(TOPICS[:5], random.randint(0, 3)),
                        'recommendations': random.choice([
                            'Рекомендуется дополнительная практика',
                            'Необходимо повторить материал',
                            'Хорошее понимание темы',
                            'Требуется консультация',
                        ]),
                    }
                )
                if created:
                    progress_count += 1
    
    print(f"  ✓ Создано записей о прогрессе: {progress_count}")
    return progress_count


def main():
    print("=" * 60)
    print("ГЕНЕРАЦИЯ ДАННЫХ ДЛЯ UNIQUEST (КАЗАХСТАН)")
    print("=" * 60)
    
    # Очистка старых данных (опционально)
    # print("\n⚠ ВНИМАНИЕ: Это удалит все существующие данные!")
    # response = input("Продолжить? (yes/no): ")
    # if response.lower() != 'yes':
    #     print("Отменено.")
    #     return
    
    try:
        # 1. Специальности
        specialties = create_specialties()
        
        # 2. Предметы
        subjects = create_subjects(specialties)
        
        # 3. Преподаватели
        teachers = create_teachers(15)
        
        # 4. Студенты
        students = create_students(200)
        
        # 5. Курсы
        courses = create_courses(subjects, teachers)
        
        # 6. Задания
        assignments = create_assignments(courses)
        
        # 7. Оценки
        grades_count = create_grades(students, courses)
        
        # 8. Расписание
        schedule = create_schedule(courses)
        
        # 9. Прогресс студентов
        progress_count = create_progress_records(students, courses)
        
        print("\n" + "=" * 60)
        print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        print(f"Специальностей: {len(specialties)}")
        print(f"Предметов: {len(subjects)}")
        print(f"Преподавателей: {len(teachers)}")
        print(f"Студентов: {len(students)}")
        print(f"Курсов: {len(courses)}")
        print(f"Заданий: {len(assignments)}")
        print(f"Оценок: {grades_count}")
        print(f"Записей расписания: {len(schedule)}")
        print(f"Записей о прогрессе: {progress_count}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

