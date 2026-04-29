from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def seed_kamila_demo_data(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("main", "Group")
    Profile = apps.get_model("main", "Profile")
    Student = apps.get_model("main", "Student")
    Course = apps.get_model("main", "Course")
    Enrollment = apps.get_model("main", "Enrollment")
    Grade = apps.get_model("main", "Grade")
    Assignment = apps.get_model("main", "Assignment")
    ScheduleEntry = apps.get_model("main", "ScheduleEntry")

    kamila = User.objects.filter(username="kamila.zholdaskyzy").first()
    teacher = User.objects.filter(username="a.lebedev").first()
    if not kamila:
        return

    current_year = timezone.now().year
    group, _ = Group.objects.get_or_create(
        name="ИС-Р",
        defaults={"year": current_year},
    )

    profile, _ = Profile.objects.get_or_create(user_id=kamila.id)
    profile.role = "student"
    profile.group_id = group.id
    profile.save()

    student, _ = Student.objects.get_or_create(
        user_id=kamila.id,
        defaults={
            "first_name": kamila.first_name or "Камила",
            "last_name": kamila.last_name or "Жолдаскызы",
            "email": kamila.email or "kamila.zholdaskyzy@student.uniquest.kz",
            "group_id": group.id,
            "is_active": True,
        },
    )
    if student.group_id != group.id:
        student.group_id = group.id
        student.save()

    courses_spec = [
        ("CS101", "Введение в программирование"),
        ("CS102", "Базы данных"),
        ("CS201", "Веб-разработка"),
    ]
    now = timezone.now()

    for idx, (code, name) in enumerate(courses_spec):
        course, _ = Course.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "description": f"Демо-курс {name}",
                "credits": 3,
                "teacher_id": teacher.id if teacher else None,
            },
        )
        if teacher and course.teacher_id != teacher.id:
            course.teacher_id = teacher.id
            course.save()

        Enrollment.objects.get_or_create(student_id=student.id, course_id=course.id)

        assignment, _ = Assignment.objects.get_or_create(
            course_id=course.id,
            title=f"Контрольная работа по курсу {name}",
            defaults={
                "description": "Автоматически созданное демо-задание для Render.",
                "due_date": now + timedelta(days=14),
                "max_score": 100,
                "topic": "Базовые темы",
                "assignment_type": "quiz",
            },
        )

        grade_value = 88 - idx * 4
        Grade.objects.get_or_create(
            student_id=kamila.id,
            course_id=course.id,
            assignment_id=assignment.id,
            assignment_name=assignment.title,
            defaults={
                "value": grade_value,
                "topic": "Базовые темы",
                "date": now - timedelta(days=idx + 1),
                "comment": "Демо-оценка для проверки интерфейса.",
            },
        )

        sched, _ = ScheduleEntry.objects.get_or_create(
            course_id=course.id,
            weekday=idx % 5,
            start_time="09:00",
            end_time="10:30",
            defaults={"classroom": "A-101"},
        )
        sched.groups.add(profile)


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0011_seed_render_test_accounts"),
    ]

    operations = [
        migrations.RunPython(seed_kamila_demo_data, migrations.RunPython.noop),
    ]

