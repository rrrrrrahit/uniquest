from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone


def seed_expanded_demo_academics(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("main", "Group")
    Profile = apps.get_model("main", "Profile")
    Specialty = apps.get_model("main", "Specialty")
    Subject = apps.get_model("main", "Subject")
    Student = apps.get_model("main", "Student")
    Course = apps.get_model("main", "Course")
    Enrollment = apps.get_model("main", "Enrollment")
    ScheduleEntry = apps.get_model("main", "ScheduleEntry")
    Assignment = apps.get_model("main", "Assignment")
    Grade = apps.get_model("main", "Grade")
    Lecture = apps.get_model("main", "Lecture")

    now = timezone.now()
    current_year = now.year
    academic_year = f"{current_year}-{current_year + 1}"

    # Teachers
    teachers_data = [
        ("a.lebedev", "Андрей", "Лебедев", "a.lebedev@uniquest.kz"),
        ("lebedev", "Андрей", "Лебедев", "lebedev@uniquest.kz"),
    ]
    teachers = []
    for username, first, last, email in teachers_data:
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                "first_name": first,
                "last_name": last,
                "email": email,
                "is_active": True,
                "is_staff": True,
            },
        )
        Profile.objects.update_or_create(
            user_id=user.id,
            defaults={"role": "teacher", "group_id": None, "specialty_id": None},
        )
        teachers.append(user)

    # Specialties
    ict_spec, _ = Specialty.objects.get_or_create(
        code="6B061",
        defaults={
            "name_kk": "Ақпараттық-коммуникациялық технологиялар",
            "name_ru": "Информационно-коммуникационные технологии",
            "description": "IT направление: программирование, данные, сети, веб.",
        },
    )
    econ_spec, _ = Specialty.objects.get_or_create(
        code="6B041",
        defaults={
            "name_kk": "Экономика және бизнес",
            "name_ru": "Экономика и бизнес",
            "description": "Экономическое направление: финансы, учет, аналитика.",
        },
    )

    # Groups
    groups_data = [
        ("IT-101", ict_spec),
        ("IT-102", ict_spec),
        ("IT-201", ict_spec),
        ("ECO-101", econ_spec),
        ("ECO-201", econ_spec),
    ]
    groups = {}
    for group_name, spec in groups_data:
        group, _ = Group.objects.get_or_create(
            name=group_name,
            defaults={"year": current_year},
        )
        groups[group_name] = (group, spec)

    # Students
    students_data = [
        ("kamila.zholdaskyzy", "Камила", "Жолдаскызы", "kamila.zholdaskyzy@student.uniquest.kz", "IT-101"),
        ("aidan.serik", "Айдан", "Серик", "aidan.serik@student.uniquest.kz", "IT-101"),
        ("daniyar.karim", "Данияр", "Карим", "daniyar.karim@student.uniquest.kz", "IT-102"),
        ("aliya.ermek", "Алия", "Ермек", "aliya.ermek@student.uniquest.kz", "IT-102"),
        ("arsen.nur", "Арсен", "Нур", "arsen.nur@student.uniquest.kz", "IT-201"),
        ("madina.ulan", "Мадина", "Улан", "madina.ulan@student.uniquest.kz", "IT-201"),
        ("timur.sapar", "Тимур", "Сапар", "timur.sapar@student.uniquest.kz", "ECO-101"),
        ("dana.bek", "Дана", "Бек", "dana.bek@student.uniquest.kz", "ECO-101"),
        ("nursultan.abai", "Нурсултан", "Абай", "nursultan.abai@student.uniquest.kz", "ECO-201"),
        ("aigerim.samat", "Айгерим", "Самат", "aigerim.samat@student.uniquest.kz", "ECO-201"),
    ]
    student_rows = []
    for idx, (username, first, last, email, group_name) in enumerate(students_data):
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                "first_name": first,
                "last_name": last,
                "email": email,
                "is_active": True,
                "password": make_password("Student2026!"),
            },
        )

        group, spec = groups[group_name]
        Profile.objects.update_or_create(
            user_id=user.id,
            defaults={
                "role": "student",
                "group_id": group.id,
                "specialty_id": spec.id,
                "enrollment_date": now.date(),
            },
        )
        student, _ = Student.objects.update_or_create(
            user_id=user.id,
            defaults={
                "first_name": first,
                "last_name": last,
                "email": email,
                "group_id": group.id,
                "is_active": True,
            },
        )
        student_rows.append((idx, user, student, group_name))

    # Subjects and courses
    subjects_data = [
        ("IT101", "Программирование 1", ict_spec),
        ("IT102", "Базы данных", ict_spec),
        ("IT201", "Веб-разработка", ict_spec),
        ("IT202", "Алгоритмы и структуры данных", ict_spec),
        ("IT203", "Сетевые технологии", ict_spec),
        ("IT204", "Кибербезопасность", ict_spec),
        ("ECO101", "Микроэкономика", econ_spec),
        ("ECO102", "Макроэкономика", econ_spec),
        ("ECO201", "Финансовый учет", econ_spec),
        ("ECO202", "Эконометрика", econ_spec),
    ]
    courses = []
    for idx, (code, title, spec) in enumerate(subjects_data):
        subject, _ = Subject.objects.get_or_create(
            code=code,
            defaults={
                "name_kk": title,
                "name_ru": title,
                "credits": 5 if code.startswith("IT") else 4,
                "specialty_id": spec.id,
            },
        )
        teacher = teachers[idx % len(teachers)]
        course, _ = Course.objects.get_or_create(
            code=code,
            defaults={
                "name": title,
                "subject_id": subject.id,
                "teacher_id": teacher.id,
                "description": f"Учебная дисциплина: {title}.",
                "credits": 5 if code.startswith("IT") else 4,
                "semester": 1 if idx % 2 == 0 else 2,
                "academic_year": academic_year,
            },
        )
        if course.teacher_id != teacher.id:
            course.teacher_id = teacher.id
            course.save(update_fields=["teacher"])
        courses.append(course)

    # Group-to-course map
    group_course_prefixes = {
        "IT-101": ("IT101", "IT102", "IT201", "ECO101"),
        "IT-102": ("IT101", "IT202", "IT203", "ECO102"),
        "IT-201": ("IT201", "IT202", "IT204", "ECO202"),
        "ECO-101": ("ECO101", "ECO102", "ECO201", "IT101"),
        "ECO-201": ("ECO102", "ECO201", "ECO202", "IT102"),
    }
    courses_by_code = {course.code: course for course in courses}

    # Enrollments, schedule links, assignments, grades, lecture materials
    for idx, user, student, group_name in student_rows:
        profile = Profile.objects.filter(user_id=user.id).first()
        if not profile:
            continue

        selected_codes = group_course_prefixes.get(group_name, ())
        for cidx, code in enumerate(selected_codes):
            course = courses_by_code.get(code)
            if not course:
                continue

            enrollment, _ = Enrollment.objects.get_or_create(
                student_id=student.id,
                course_id=course.id,
            )

            assignment, _ = Assignment.objects.get_or_create(
                course_id=course.id,
                title=f"Промежуточная работа: {course.name}",
                defaults={
                    "description": "Автосозданное задание для демо-режима Render.",
                    "due_date": now + timedelta(days=14 + cidx),
                    "max_score": 100,
                    "topic": "Ключевые темы курса",
                    "assignment_type": "quiz",
                },
            )

            base = 92 - (idx % 5) * 4 - cidx
            value = max(65, min(98, base))
            Grade.objects.get_or_create(
                student_id=user.id,
                course_id=course.id,
                enrollment_id=enrollment.id,
                assignment_id=assignment.id,
                assignment_name=assignment.title,
                defaults={
                    "value": Decimal(str(value)),
                    "topic": "Ключевые темы курса",
                    "date": now - timedelta(days=idx + cidx + 2),
                    "comment": "Демо-оценка для панели преподавателя и студента.",
                },
            )

            schedule, _ = ScheduleEntry.objects.get_or_create(
                course_id=course.id,
                weekday=(cidx + idx) % 5,
                start_time="09:00",
                end_time="10:30",
                defaults={"classroom": f"B-{100 + cidx}"},
            )
            schedule.groups.add(profile)

            Lecture.objects.get_or_create(
                course_id=course.id,
                title=f"Методические материалы: {course.name}",
                defaults={
                    "content_text": (
                        f"План темы по дисциплине {course.name}.\n"
                        f"1) Теория\n2) Практика\n3) Контрольные вопросы"
                    ),
                    "content_url": "https://uniquest.kz/materials",
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0012_seed_kamila_demo_data"),
    ]

    operations = [
        migrations.RunPython(seed_expanded_demo_academics, migrations.RunPython.noop),
    ]

