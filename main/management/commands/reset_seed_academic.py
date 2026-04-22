from datetime import date, datetime, time, timedelta
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from main.models import (
    Assignment,
    Attendance,
    Course,
    Enrollment,
    ExamPrediction,
    Grade,
    Group,
    Lecture,
    PersonalizedStudyPlan,
    ProblemPrediction,
    Profile,
    Recommendation,
    ScheduleEntry,
    SmartLearningProfile,
    Specialty,
    Student,
    StudentProgress,
    Subject,
    Submission,
)


class Command(BaseCommand):
    help = "Полностью очищает БД и заполняет сценарий преподавателя/студентов для демо."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(2026)
        self._wipe_data()
        context = self._create_core_entities()
        self._create_teacher_tracks(context)
        self._create_kamila_academic_track(context)
        self._create_attendance_and_grades(context)
        self._print_credentials(context)

    def _wipe_data(self):
        self.stdout.write(self.style.WARNING("Очистка данных..."))
        ProblemPrediction.objects.all().delete()
        Recommendation.objects.all().delete()
        Submission.objects.all().delete()
        Grade.objects.all().delete()
        Attendance.objects.all().delete()
        PersonalizedStudyPlan.objects.all().delete()
        ExamPrediction.objects.all().delete()
        SmartLearningProfile.objects.all().delete()
        StudentProgress.objects.all().delete()
        Assignment.objects.all().delete()
        Lecture.objects.all().delete()
        ScheduleEntry.objects.all().delete()
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Subject.objects.all().delete()
        Specialty.objects.all().delete()
        Student.objects.all().delete()
        Profile.objects.all().delete()
        Group.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Старые данные удалены."))

    def _create_user(self, username, first_name, last_name, email, password, role, group=None, is_staff=False):
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_staff=is_staff,
            is_active=True,
        )
        user.set_password(password)
        user.save()
        profile = Profile.objects.get(user=user)
        profile.role = role
        profile.group = group
        profile.save(update_fields=["role", "group"])
        return user

    def _create_student(self, username, first_name, last_name, email, password, group):
        user = self._create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=Profile.ROLE_STUDENT,
            group=group,
            is_staff=False,
        )
        student = Student.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            group=group,
            dob=date(2005, random.randint(1, 12), random.randint(1, 28)),
            is_active=True,
        )
        return user, student

    def _create_core_entities(self):
        specialty = Specialty.objects.create(
            code="6B061",
            name_kk="Ақпараттық-коммуникациялық технологиялар",
            name_ru="Информационно-коммуникационные технологии",
            description="Демонстрационный профиль для академического сценария.",
        )

        groups = {
            "ИС-Р": Group.objects.create(name="ИС-Р", year=2024),
            "ИС-К": Group.objects.create(name="ИС-К", year=2024),
            "ВТиПО-Р": Group.objects.create(name="ВТиПО-Р", year=2024),
        }

        teacher_user = self._create_user(
            username="a.lebedev",
            first_name="Андрей",
            last_name="Лебедев",
            email="a.lebedev@uniquest.kz",
            password="Teacher2026!",
            role=Profile.ROLE_TEACHER,
            group=None,
            is_staff=True,
        )

        subject_defs = [
            ("ADS301", "Алгоритмдер және деректер құрылымы", "Алгоритмы и структуры данных", 5),
            ("DB302", "Деректер қорларын жобалау және әкімшілендіру", "Проектирование и администрирование баз данных", 5),
            ("CYB303", "Киберқауіпсіздік негіздері", "Основы кибербезопасности", 4),
            ("ENG210", "Академиялық ағылшын тілі", "Академический английский язык", 4),
            ("ECO220", "Экономикалық теория", "Экономическая теория", 4),
            ("HIS230", "Қазақстанның қазіргі заман тарихы", "История Казахстана и современности", 4),
        ]
        subjects = {}
        for code, kk, ru, credits in subject_defs:
            subjects[code] = Subject.objects.create(
                code=code,
                name_kk=kk,
                name_ru=ru,
                credits=credits,
                specialty=specialty,
            )

        courses = {
            "ads": Course.objects.create(
                name="Алгоритмы и структуры данных",
                code="CS-ADS-301",
                subject=subjects["ADS301"],
                teacher=teacher_user,
                description="Алгоритмический анализ, структуры хранения данных и оценка сложности.",
                credits=5,
                semester=2,
                academic_year="2025-2026",
            ),
            "db": Course.objects.create(
                name="Проектирование и администрирование баз данных",
                code="CS-DB-302",
                subject=subjects["DB302"],
                teacher=teacher_user,
                description="Архитектура реляционных БД, оптимизация запросов и обеспечение целостности.",
                credits=5,
                semester=2,
                academic_year="2025-2026",
            ),
            "cyber": Course.objects.create(
                name="Основы кибербезопасности",
                code="CS-CYB-303",
                subject=subjects["CYB303"],
                teacher=teacher_user,
                description="Модели угроз, управление доступом и практики защиты инфраструктуры.",
                credits=4,
                semester=2,
                academic_year="2025-2026",
            ),
        }

        # Дополнительные преподаватели для персонального трека Камилы
        eng_teacher = self._create_user(
            username="n.smirnova",
            first_name="Надежда",
            last_name="Смирнова",
            email="n.smirnova@uniquest.kz",
            password="Teacher2026!",
            role=Profile.ROLE_TEACHER,
            is_staff=True,
        )
        eco_teacher = self._create_user(
            username="t.nurganbetov",
            first_name="Талгат",
            last_name="Нурганбетов",
            email="t.nurganbetov@uniquest.kz",
            password="Teacher2026!",
            role=Profile.ROLE_TEACHER,
            is_staff=True,
        )
        his_teacher = self._create_user(
            username="e.ivanova",
            first_name="Екатерина",
            last_name="Иванова",
            email="e.ivanova@uniquest.kz",
            password="Teacher2026!",
            role=Profile.ROLE_TEACHER,
            is_staff=True,
        )

        courses["eng"] = Course.objects.create(
            name="Академический английский язык",
            code="HUM-ENG-210",
            subject=subjects["ENG210"],
            teacher=eng_teacher,
            description="Профессиональная академическая коммуникация на английском языке.",
            credits=4,
            semester=2,
            academic_year="2025-2026",
        )
        courses["eco"] = Course.objects.create(
            name="Экономическая теория",
            code="SOC-ECO-220",
            subject=subjects["ECO220"],
            teacher=eco_teacher,
            description="Фундаментальные модели микро- и макроэкономики.",
            credits=4,
            semester=2,
            academic_year="2025-2026",
        )
        courses["his"] = Course.objects.create(
            name="История Казахстана и современности",
            code="HUM-HIS-230",
            subject=subjects["HIS230"],
            teacher=his_teacher,
            description="Исторические этапы развития Казахстана и современные общественные процессы.",
            credits=4,
            semester=2,
            academic_year="2025-2026",
        )

        students_by_group = {
            "ИС-Р": [
                ("nikita.panin", "Никита", "Панин"),
                ("asylbek.omarov", "Асылбек", "Омаров"),
                ("darya.kuzmina", "Дарья", "Кузьмина"),
                ("madi.sadykov", "Мади", "Садыков"),
                ("elena.baranova", "Елена", "Баранова"),
                ("ruslan.kerimov", "Руслан", "Керимов"),
            ],
            "ИС-К": [
                ("ivan.shcherbakov", "Иван", "Щербаков"),
                ("dinara.sarsembayeva", "Динара", "Сарсембаева"),
                ("oleg.belov", "Олег", "Белов"),
                ("aizhan.kadyrbek", "Айжан", "Кадырбек"),
                ("sultan.kaliyev", "Султан", "Калиев"),
                ("polina.gromova", "Полина", "Громова"),
            ],
            "ВТиПО-Р": [
                ("aidar.sarsembay", "Айдар", "Сарсембай"),
                ("vadim.zorin", "Вадим", "Зорин"),
                ("aliya.saken", "Алия", "Сәкен"),
                ("maksim.egorov", "Максим", "Егоров"),
                ("gulmira.amanzhol", "Гульмира", "Аманжол"),
            ],
        }

        all_students = []
        for group_name, rows in students_by_group.items():
            for username, first_name, last_name in rows:
                user, student = self._create_student(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=f"{username}@student.uniquest.kz",
                    password="Student2026!",
                    group=groups[group_name],
                )
                all_students.append((user, student))

        kamila_user, kamila_student = self._create_student(
            username="kamila.zholdaskyzy",
            first_name="Камила",
            last_name="Жолдаскызы",
            email="kamila.zholdaskyzy@student.uniquest.kz",
            password="Kamila2026!",
            group=groups["ВТиПО-Р"],
        )
        all_students.append((kamila_user, kamila_student))

        return {
            "specialty": specialty,
            "groups": groups,
            "teacher_user": teacher_user,
            "courses": courses,
            "all_students": all_students,
            "kamila_user": kamila_user,
            "kamila_student": kamila_student,
        }

    def _create_teacher_tracks(self, context):
        groups = context["groups"]
        courses = context["courses"]

        # Все студенты групп закрепляются за предметами основного преподавателя.
        for _, student in context["all_students"]:
            for course_key in ("ads", "db", "cyber"):
                Enrollment.objects.create(
                    student=student,
                    course=courses[course_key],
                    enrolled_at=datetime(2026, 3, 1, 10, 0),
                )

        schedule_def = [
            ("ads", 0, time(9, 0), time(10, 30), "ЛК-201", "ИС-Р"),
            ("db", 1, time(11, 0), time(12, 30), "ЛК-310", "ИС-К"),
            ("cyber", 2, time(13, 0), time(14, 30), "ЛАБ-105", "ВТиПО-Р"),
            ("ads", 3, time(10, 40), time(12, 10), "ЛК-204", "ВТиПО-Р"),
            ("db", 4, time(9, 0), time(10, 30), "ЛАБ-302", "ИС-Р"),
            ("cyber", 4, time(14, 40), time(16, 10), "ЛАБ-108", "ИС-К"),
        ]

        for course_key, weekday, start, end, room, group_name in schedule_def:
            entry = ScheduleEntry.objects.create(
                course=courses[course_key],
                weekday=weekday,
                start_time=start,
                end_time=end,
                classroom=room,
            )
            profiles = Profile.objects.filter(group=groups[group_name], role=Profile.ROLE_STUDENT)
            entry.groups.add(*profiles)

    def _create_kamila_academic_track(self, context):
        courses = context["courses"]
        kamila_student = context["kamila_student"]
        kamila_profile = Profile.objects.get(user=context["kamila_user"])

        # Камилу дополнительно записываем на дисциплины с разными преподавателями.
        for course_key in ("eng", "eco", "his"):
            Enrollment.objects.create(
                student=kamila_student,
                course=courses[course_key],
                enrolled_at=datetime(2026, 3, 1, 10, 0),
            )

        personal_schedule = [
            ("eng", 0, time(14, 40), time(16, 10), "ГУМ-114"),
            ("eco", 2, time(10, 40), time(12, 10), "ЭК-212"),
            ("his", 3, time(13, 0), time(14, 30), "ГУМ-105"),
        ]
        for course_key, weekday, start, end, room in personal_schedule:
            entry = ScheduleEntry.objects.create(
                course=courses[course_key],
                weekday=weekday,
                start_time=start,
                end_time=end,
                classroom=room,
            )
            entry.groups.add(kamila_profile)

    def _create_attendance_and_grades(self, context):
        start_dt = date(2026, 3, 1)
        end_dt = date(2026, 5, 15)
        courses = context["courses"]

        course_topics = {
            "ads": ["Динамические структуры данных", "Рекурсивные алгоритмы", "Оценка сложности"],
            "db": ["Нормализация", "Транзакции и ACID", "Оптимизация SQL-запросов"],
            "cyber": ["Управление доступом", "Сетевые атаки", "Криптографические протоколы"],
            "eng": ["Academic Writing", "Presentation Skills", "Critical Reading"],
            "eco": ["Спрос и предложение", "Макроэкономическое равновесие", "Инфляционные процессы"],
            "his": ["Исторические этапы Казахстана", "Индустриализация", "Современные реформы"],
        }

        course_assignments = {}
        course_lectures = {}
        for course_key, course in courses.items():
            assignments = []
            lectures = []
            for idx in range(4):
                due_date = datetime(2026, 3, 12, 18, 0) + timedelta(days=18 * idx)
                assignment = Assignment.objects.create(
                    course=course,
                    title=f"Модульная работа {idx + 1}",
                    description=f"Оценочная работа по теме: {course_topics[course_key][idx % 3]}",
                    due_date=due_date,
                    max_score=100,
                    topic=course_topics[course_key][idx % 3],
                    assignment_type="quiz" if idx % 2 else "lab",
                )
                assignments.append(assignment)

            lecture_dates = [date(2026, 3, 5), date(2026, 3, 19), date(2026, 4, 2), date(2026, 4, 16), date(2026, 5, 7)]
            for idx, lec_date in enumerate(lecture_dates, start=1):
                lecture = Lecture.objects.create(
                    course=course,
                    title=f"Лекция {idx}: {course_topics[course_key][(idx - 1) % 3]}",
                    content_text=f"Разбор академической темы: {course_topics[course_key][(idx - 1) % 3]}",
                )
                Lecture.objects.filter(id=lecture.id).update(
                    created_at=datetime.combine(lec_date, time(9, 0))
                )
                lecture.refresh_from_db()
                lectures.append(lecture)

            course_assignments[course_key] = assignments
            course_lectures[course_key] = lectures

        # Профили успеваемости по группам для реалистичного риска.
        def grade_band(student):
            if student.user.username == "kamila.zholdaskyzy":
                return {"ads": 84, "db": 79, "cyber": 81, "eng": 93, "eco": 88, "his": 91}
            if student.group.name == "ИС-Р":
                return {"ads": 85, "db": 82, "cyber": 80}
            if student.group.name == "ИС-К":
                return {"ads": 73, "db": 69, "cyber": 72}
            return {"ads": 78, "db": 75, "cyber": 77}

        feedback_map = [
            "Хорошая динамика, сохраняйте темп.",
            "Есть прогресс, усилить работу с теорией.",
            "Стабильная работа, важно не пропускать дедлайны.",
            "Рекомендуется дополнительно проработать проблемные темы.",
            "Отличный результат, высокий уровень академической самостоятельности.",
        ]

        enrollments = Enrollment.objects.select_related("student__user", "student__group", "course")
        for enrollment in enrollments:
            student = enrollment.student
            user = student.user
            if not user:
                continue

            # Переводим код курса в ключ.
            course_key = None
            for key, course in courses.items():
                if course.id == enrollment.course_id:
                    course_key = key
                    break
            if not course_key:
                continue

            base = grade_band(student).get(course_key, 76)
            assignments = course_assignments[course_key]
            lectures = course_lectures[course_key]

            # Submissions + Grades
            for idx, assignment in enumerate(assignments):
                # Для группы ИС-К часть заданий не сдана, чтобы отразить риски.
                should_submit = True
                if student.group and student.group.name == "ИС-К" and idx == 1:
                    should_submit = False

                if should_submit:
                    submission = Submission.objects.create(
                        assignment=assignment,
                        student=user,
                        text=f"Выполнение задания по теме: {assignment.topic}",
                        score=max(45, min(100, base + random.randint(-8, 8))),
                    )
                    submitted_dt = datetime(2026, 3, 13, 12, 0) + timedelta(days=18 * idx)
                    Submission.objects.filter(id=submission.id).update(submitted_at=submitted_dt)

                value = max(45, min(100, base + random.randint(-10, 10)))
                grade_date = datetime(2026, 3, 15, 12, 0) + timedelta(days=18 * idx)
                if grade_date.date() > end_dt:
                    grade_date = datetime(2026, 5, 14, 12, 0)
                Grade.objects.create(
                    student=user,
                    course=enrollment.course,
                    enrollment=enrollment,
                    assignment=assignment,
                    assignment_name=assignment.title,
                    value=value,
                    date=grade_date,
                    topic=assignment.topic,
                    comment=feedback_map[(idx + len(user.username)) % len(feedback_map)],
                )

            # Дополнительная контрольная на конце периода
            Grade.objects.create(
                student=user,
                course=enrollment.course,
                enrollment=enrollment,
                assignment_name="Итоговый срез (15 мая)",
                value=max(45, min(100, base + random.randint(-7, 7))),
                date=datetime(2026, 5, 15, 11, 0),
                topic=course_topics[course_key][0],
                comment="Итог за период с 1 марта по 15 мая.",
            )

            # Attendance
            for lecture in lectures:
                present = True
                if student.group and student.group.name == "ИС-К":
                    present = random.random() > 0.28
                elif student.group and student.group.name == "ВТиПО-Р":
                    present = random.random() > 0.15
                else:
                    present = random.random() > 0.08
                Attendance.objects.create(
                    enrollment=enrollment,
                    lecture=lecture,
                    date=lecture.created_at.date(),
                    present=present,
                )

    def _print_credentials(self, context):
        teacher = context["teacher_user"]
        kamila = context["kamila_user"]
        self.stdout.write(self.style.SUCCESS("\nГотово: база очищена и заполнена новым набором данных."))
        self.stdout.write(self.style.SUCCESS("Основной преподаватель:"))
        self.stdout.write(f"  Логин: {teacher.username}")
        self.stdout.write("  Пароль: Teacher2026!")
        self.stdout.write("  Предметы: Базы данных, Алгоритмы и структуры данных, Кибербезопасность")
        self.stdout.write(self.style.SUCCESS("Студентка:"))
        self.stdout.write(f"  Логин: {kamila.username}")
        self.stdout.write("  Пароль: Kamila2026!")
