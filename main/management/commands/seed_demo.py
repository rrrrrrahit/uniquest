import random
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User

from main.models import (
    Group,
    Student,
    Course,
    Lecture,
    ScheduleEntry,
    Enrollment,
    Grade,
    Attendance,
    Profile,
)


BASE_DIR = Path(__file__).resolve().parents[3]
SEED_LOG_FILE = BASE_DIR / "seed_log.txt"


KZ_FIRST_NAMES = [
    "Айдан", "Нурлан", "Данияр", "Азамат", "Ерлан", "Асылбек", "Дамир",
    "Айбек", "Рустем", "Алмаз", "Бахтияр", "Жанат", "Марат", "Тимур",
    "Асыл", "Айгуль", "Алина", "Дана", "Асель", "Гульнара", "Сабина",
    "Амина", "Айша", "Аружан", "Динара", "Малика", "Жанара", "Мария",
    "Анна", "Елена", "Ольга", "Наталья", "Татьяна",
]

KZ_LAST_NAMES = [
    "Қасымов", "Ахметов", "Омаров", "Ермеков", "Смагулов", "Нуртазин",
    "Абдуллаев", "Сапарбеков", "Токтаров", "Калиев", "Мамедов", "Ибрагимов",
    "Усенов", "Байжанов", "Жумабеков", "Касымова", "Ахметова", "Омарова",
    "Ермекова", "Смагулова", "Нуртазина", "Абдуллаева", "Сапарбекова",
    "Токтарова", "Калиева", "Мамедова", "Ибрагимова", "Петров", "Иванов",
    "Сидоров", "Кузнецов", "Смирнов", "Попов",
]


COURSE_CODES = [
    "CS101", "CS102", "CS201", "CS202", "CS301", "CS302",
    "MATH101", "MATH201", "MATH301",
    "PHY101", "PHY201",
    "ML401", "AI402",
    "WEB201", "WEB301",
    "DB201", "DB301",
    "SE201", "SE301",
    "NET201", "SEC301",
    "HCI201", "UX301",
    "STAT201", "STAT301",
]

ROOMS = ["A-101", "A-202", "B-301", "B-402", "C-105", "C-206", "D-307"]

LOREM_PARAGRAPHS = [
    "Эта лекция посвящена основам программирования на языке Python. "
    "Мы рассмотрим базовые конструкции, типы данных и структуры управления.",
    "На занятии обсуждаются лучшие практики разработки: использование Git, "
    "код-ревью и непрерывная интеграция.",
    "В этой лекции разбираются алгоритмы сортировки и поиска, а также их "
    "сложность по времени и памяти.",
    "Материал лекции охватывает основы машинного обучения: линейная регрессия, "
    "логистическая регрессия и метрики качества моделей.",
    "Рассматриваются принципы проектирования реляционных баз данных, нормализация "
    "и оптимизация запросов.",
]

DEFAULT_STUDENT_PASSWORD = "Student2025!"
SPECIAL_STUDENT_PASSWORD = "Suraya2025!"
SPECIAL_TEACHER_PASSWORD = "Teacher2025!"
SPECIAL_GROUP_NAME = "VTPO-MAG-22"


def log_line(message: str) -> None:
    timestamp = datetime.utcnow().isoformat()
    with SEED_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


class Command(BaseCommand):
    help = (
        "Заполняет базу демонстрационными данными: студенты, группы, курсы, "
        "расписание, лекции, оценки и посещаемость."
    )

    def add_arguments(self, parser):
        parser.add_argument("--students", type=int, default=500)
        parser.add_argument("--groups", type=int, default=20)
        parser.add_argument("--courses", type=int, default=30)
        parser.add_argument("--seed", type=int, default=42)

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        students_target = options["students"]
        groups_target = options["groups"]
        courses_target = options["courses"]

        self.stdout.write(self.style.MIGRATE_HEADING("=== UniQuest demo seeding ==="))
        log_line("Начало seed_demo")

        groups = self._create_groups(groups_target)
        courses = self._create_courses(courses_target)
        students = self._create_students(students_target, groups)
        enrollments = self._create_enrollments(students, courses)
        self._create_schedule(groups, courses)
        lectures = self._create_lectures(courses)
        self._create_attendance_and_grades(enrollments, lectures)
        self._ensure_special_demo_data()

        summary = (
            f"Групп: {len(groups)}, курсов: {len(courses)}, студентов: {len(students)}, "
            f"записей на курсы: {len(enrollments)}, лекций: {len(lectures)}"
        )
        self.stdout.write(self.style.SUCCESS(summary))
        log_line(f"Успешное завершение seed_demo. {summary}")

    def _rand_past_datetime(self, days_back: int = 365) -> datetime:
        offset = random.randint(0, days_back)
        return timezone.now() - timedelta(days=offset)

    def _create_groups(self, count: int):
        groups = []
        base_year = timezone.now().year
        for i in range(count):
            name = f"CS-{101 + i}"
            year = base_year - random.randint(0, 3)
            group, _ = Group.objects.get_or_create(name=name, defaults={"year": year})
            groups.append(group)
        self.stdout.write(f"Создано/найдено групп: {len(groups)}")
        log_line(f"Группы: {len(groups)}")
        return groups

    def _create_courses(self, count: int):
        courses = []
        used_codes = set()
        for i in range(count):
            code = COURSE_CODES[i % len(COURSE_CODES)]
            if code in used_codes:
                code = f"{code}-{i}"
            used_codes.add(code)
            title = f"Курс {code}"
            description = (
                "Демонстрационный курс UniQuest, включающий лекции, задания и оценки."
            )
            course, _ = Course.objects.get_or_create(
                code=code,
                defaults={
                    "name": title,
                    "description": description,
                    "credits": random.choice([2, 3, 4]),
                },
            )
            courses.append(course)
        self.stdout.write(f"Создано/найдено курсов: {len(courses)}")
        log_line(f"Курсы: {len(courses)}")
        return courses

    def _create_students(self, count: int, groups):
        students = []
        existing_emails = set(
            Student.objects.values_list("email", flat=True)
        )
        for i in range(count):
            first_name = random.choice(KZ_FIRST_NAMES)
            last_name = random.choice(KZ_LAST_NAMES)
            base_email = f"{first_name.lower()}.{last_name.lower()}@student.uniquest.kz"
            email = base_email
            idx = 1
            while email in existing_emails:
                email = f"{first_name.lower()}.{last_name.lower()}{idx}@student.uniquest.kz"
                idx += 1
            existing_emails.add(email)

            group = random.choice(groups) if groups else None
            username = f"student_{i+1:04d}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(DEFAULT_STUDENT_PASSWORD)
                user.save()
            else:
                changed = False
                if user.email != email:
                    user.email = email
                    changed = True
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    changed = True
                if changed:
                    user.save()

            Profile.objects.update_or_create(
                user=user,
                defaults={
                    "role": Profile.ROLE_STUDENT,
                    "group": group.name if group else "",
                    "bio": f"Студент {group.name if group else 'без группы'}",
                    "phone": f"+7{random.randint(7000000000, 7999999999)}",
                },
            )

            student, _ = Student.objects.update_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "group": group,
                    "dob": timezone.now().date()
                    - timedelta(days=18 * 365 + random.randint(0, 365)),
                    "is_active": True,
                    "user": user,
                },
            )
            students.append(student)
        self.stdout.write(f"Создано/найдено студентов: {len(students)}")
        log_line(f"Студенты: {len(students)}")
        return students

    def _create_enrollments(self, students, courses):
        from main.models import Enrollment  # локальный импорт во избежание циклов

        enrollments = []
        for student in students:
            if not courses:
                break
            k = random.randint(4, 6)
            student_courses = random.sample(courses, min(k, len(courses)))
            for course in student_courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={"enrolled_at": self._rand_past_datetime(365)},
                )
                if created:
                    enrollments.append(enrollment)
        self.stdout.write(f"Создано записей на курсы: {len(enrollments)}")
        log_line(f"Записи на курсы: {len(enrollments)}")
        return enrollments

    def _create_schedule(self, groups, courses):
        weekdays = [0, 1, 2, 3, 4]  # Пн–Пт
        time_slots = [
            ("09:00", "10:30"),
            ("10:40", "12:10"),
            ("13:00", "14:30"),
            ("14:40", "16:10"),
        ]
        created = 0
        for group in groups:
            group_courses = random.sample(
                courses, min(random.randint(3, 6), len(courses))
            )
            for course in group_courses:
                weekday = random.choice(weekdays)
                start_str, end_str = random.choice(time_slots)
                entry, made = ScheduleEntry.objects.get_or_create(
                    course=course,
                    weekday=weekday,
                    start_time=start_str,
                    end_time=end_str,
                    defaults={"classroom": random.choice(ROOMS)},
                )
                if made:
                    if group:
                        # Получаем профили студентов этой группы
                        related_profiles = Profile.objects.filter(group=group, role=Profile.ROLE_STUDENT)
                        if related_profiles.exists():
                            entry.groups.add(*related_profiles[:10])
                    created += 1
        self.stdout.write(f"Создано элементов расписания: {created}")
        log_line(f"Расписание: {created}")

    def _create_lectures(self, courses):
        lectures = []
        total_target = 2000
        per_course = max(1, total_target // max(1, len(courses)))
        for course in courses:
            created_for_course = 0
            base_date = self._rand_past_datetime(200)
            for i in range(per_course):
                title = f"{course.code} Лекция {i + 1}"
                content_text = random.choice(LOREM_PARAGRAPHS)
                content_url = None
                if random.random() < 0.3:
                    content_url = f"https://uniquest.kz/courses/{course.code.lower()}/lectures/{i+1}/"
                lecture, _ = Lecture.objects.get_or_create(
                    course=course,
                    title=title,
                    defaults={
                        "content_text": content_text,
                        "content_url": content_url,
                        "created_at": base_date + timedelta(days=i * 3),
                    },
                )
                lectures.append(lecture)
                created_for_course += 1
        self.stdout.write(f"Создано/найдено лекций: {len(lectures)}")
        log_line(f"Лекции: {len(lectures)}")
        return lectures

    def _create_attendance_and_grades(self, enrollments, lectures):
        lectures_by_course = {}
        for lec in lectures:
            lectures_by_course.setdefault(lec.course_id, []).append(lec)

        grades_created = 0
        attendance_created = 0
        for enrollment in enrollments:
            course_lectures = lectures_by_course.get(enrollment.course_id, [])
            if not course_lectures:
                continue

            # Посещаемость
            presence_prob = random.uniform(0.7, 1.0)
            for lec in course_lectures[:20]:
                present = random.random() < presence_prob
                Attendance.objects.get_or_create(
                    enrollment=enrollment,
                    lecture=lec,
                    date=lec.created_at.date(),
                    defaults={"present": present},
                )
                attendance_created += 1

            # Оценки: несколько домашних, один midterm и один финал
            hw_count = random.randint(3, 6)
            base_date = enrollment.enrolled_at
            student_user = getattr(enrollment.student, "user", None)
            if not student_user:
                continue
            for i in range(hw_count):
                grade_date = base_date + timedelta(days=14 * (i + 1))
                value = random.uniform(60, 100)
                Grade.objects.create(
                    student=student_user,
                    course=enrollment.course,
                    enrollment=enrollment,
                    assignment_name=f"Домашнее задание {i + 1}",
                    value=round(value, 2),
                    date=grade_date,
                    date_recorded=grade_date,
                    topic="Домашние задания",
                )
                grades_created += 1

            # Midterm
            midterm_date = base_date + timedelta(days=90)
            midterm_value = random.uniform(50, 100)
            Grade.objects.create(
                student=student_user,
                course=enrollment.course,
                enrollment=enrollment,
                assignment_name="Midterm",
                value=round(midterm_value, 2),
                date=midterm_date,
                date_recorded=midterm_date,
                topic="Midterm",
            )
            grades_created += 1

            # Финальный экзамен
            final_date = base_date + timedelta(days=150)
            final_value = random.uniform(50, 100)
            Grade.objects.create(
                student=student_user,
                course=enrollment.course,
                enrollment=enrollment,
                assignment_name="Финальный экзамен",
                value=round(final_value, 2),
                date=final_date,
                date_recorded=final_date,
                topic="Финал",
            )
            grades_created += 1

        self.stdout.write(
            f"Создано посещаемости: {attendance_created}, оценок: {grades_created}"
        )
        log_line(
            f"Посещаемость: {attendance_created}, оценки: {grades_created}"
        )

    def _ensure_special_demo_data(self):
        """Создает реалистичные данные для магистрантки С. Айдиновой и преподавателя М. Жасұзақовой."""
        group, _ = Group.objects.get_or_create(
            name=SPECIAL_GROUP_NAME,
            defaults={"year": timezone.now().year - 1},
        )

        teacher_user, created = User.objects.get_or_create(
            username="m.zhasuzakova",
            defaults={
                "first_name": "Мейрамкүл",
                "last_name": "Жасұзаққызы",
                "email": "meyramkul.zhasuzakova@uniquest.kz",
                "is_active": True,
                "is_staff": True,
            },
        )
        teacher_user.set_password(SPECIAL_TEACHER_PASSWORD)
        teacher_user.save()

        Profile.objects.update_or_create(
            user=teacher_user,
            defaults={
                "role": Profile.ROLE_TEACHER,
                "bio": "Преподаватель дисциплин магистратуры по направлению «Вычислительная техника и ПО».",
            },
        )

        courses_data = [
            {
                "code": "VTPO701",
                "name": "Проектирование информационных систем с использованием современных СУБД",
                "description": "Практико-ориентированный курс по проектированию и эксплуатации корпоративных СУБД.",
                "weekday": 1,
                "start": "10:00",
                "end": "11:30",
                "room": "М-402",
            },
            {
                "code": "VTPO702",
                "name": "Технологии программной инженерии",
                "description": "Глубокое изучение жизненного цикла ПО, DevOps-практик и инструментов качества.",
                "weekday": 4,
                "start": "14:00",
                "end": "15:30",
                "room": "Инкубатор 203",
            },
        ]

        highlighted_courses = []
        for data in courses_data:
            course, _ = Course.objects.get_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "credits": 5,
                    "teacher": teacher_user,
                },
            )
            if course.teacher != teacher_user:
                course.teacher = teacher_user
                course.save()
            highlighted_courses.append(course)

            schedule_entry, _ = ScheduleEntry.objects.update_or_create(
                course=course,
                group=group,
                weekday=data["weekday"],
                start_time=data["start"],
                end_time=data["end"],
                defaults={"classroom": data["room"]},
            )
            related_profiles = Profile.objects.filter(group=group.name)
            if related_profiles.exists():
                schedule_entry.groups.set(related_profiles)

        student_user, created = User.objects.get_or_create(
            username="suraya",
            defaults={
                "first_name": "Сурея",
                "last_name": "Айдинова",
                "email": "suraya.aydinova@uniquest.kz",
                "is_active": True,
            },
        )
        student_user.set_password(SPECIAL_STUDENT_PASSWORD)
        student_user.save()

        Profile.objects.update_or_create(
            user=student_user,
            defaults={
                "role": Profile.ROLE_STUDENT,
                "group": group.name,
                "bio": "Магистрантка 2 курса по специальности «Вычислительная техника и ПО».",
            },
        )

        student_obj, _ = Student.objects.update_or_create(
            email=student_user.email,
            defaults={
                "first_name": "Сурея",
                "last_name": "Айдинова",
                "group": group,
                "dob": timezone.now().date() - timedelta(days=24 * 365),
                "is_active": True,
                "user": student_user,
            },
        )

        special_enrollments = []
        for course in highlighted_courses:
            enrollment, _ = Enrollment.objects.get_or_create(
                student=student_obj,
                course=course,
                defaults={"enrolled_at": timezone.now() - timedelta(days=120)},
            )
            special_enrollments.append(enrollment)

        lectures_content = [
            (
                highlighted_courses[0],
                "Практика моделирования процессов",
                "Разбор нотаций BPMN и построение моделей для учебного кейса.",
            ),
            (
                highlighted_courses[0],
                "Оптимизация запросов в PostgreSQL",
                "На реальных примерах сравниваем планы выполнения и индексные стратегии.",
            ),
            (
                highlighted_courses[1],
                "Инженерные практики DevOps",
                "Observability, CI/CD и шаблоны внедрения в крупных командах.",
            ),
        ]

        created_lectures = []
        for course, title, content in lectures_content:
            lecture, _ = Lecture.objects.get_or_create(
                course=course,
                title=title,
                defaults={"content_text": content},
            )
            created_lectures.append(lecture)

        for enrollment in special_enrollments:
            student_user = enrollment.student.user
            for kind, value, topic in [
                ("Исследование кейса", 94, "Практика проектирования"),
                ("Проектная работа", 96, "Командный проект"),
                ("Финальный экзамен", 92, "Итог"),
            ]:
                Grade.objects.update_or_create(
                    enrollment=enrollment,
                    assignment_name=kind,
                    defaults={
                        "student": student_user,
                        "course": enrollment.course,
                        "value": value,
                        "topic": topic,
                        "date": timezone.now() - timedelta(days=random.randint(10, 40)),
                        "comment": "Данные с демонстрационной сессии.",
                    },
                )

        for enrollment in special_enrollments:
            for lecture in created_lectures:
                if lecture.course != enrollment.course:
                    continue
                Attendance.objects.update_or_create(
                    enrollment=enrollment,
                    lecture=lecture,
                    date=lecture.created_at.date() if lecture.created_at else timezone.now().date(),
                    defaults={"present": True},
                )

        log_line("Добавлены специальные данные для Айдиновой С. Р. и Жасұзаковой М. Ж.")
        self.stdout.write("Добавлены персональные данные: Айдинова С. Р. и Жасұзакова М. Ж.")


