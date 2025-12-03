from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.contrib.postgres.fields import ArrayField


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_specialty_alter_assignment_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Группа"
                    ),
                ),
                ("year", models.IntegerField(verbose_name="Год набора")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
            ],
            options={
                "verbose_name": "Группа",
                "verbose_name_plural": "Группы",
                "ordering": ["-year", "name"],
            },
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=150, verbose_name="Имя"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=150, verbose_name="Фамилия"),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="Email"
                    ),
                ),
                (
                    "dob",
                    models.DateField(
                        blank=True, null=True, verbose_name="Дата рождения"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активен"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Создан"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Обновлён"
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="students",
                        to="main.group",
                        verbose_name="Группа",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Студент",
                "verbose_name_plural": "Студенты",
            },
        ),
        migrations.CreateModel(
            name="Lecture",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="Название"),
                ),
                (
                    "content_text",
                    models.TextField(verbose_name="Содержимое"),
                ),
                (
                    "content_url",
                    models.URLField(
                        blank=True,
                        max_length=500,
                        null=True,
                        verbose_name="Ссылка на ресурс",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Создано"
                    ),
                ),
                (
                    "vector_embedding",
                    ArrayField(
                        base_field=models.FloatField(),
                        blank=True,
                        null=True,
                        size=None,
                        verbose_name="Векторное представление",
                    ),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lectures",
                        to="main.course",
                        verbose_name="Курс",
                    ),
                ),
            ],
            options={
                "verbose_name": "Лекция / ресурс",
                "verbose_name_plural": "Лекции / ресурсы",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="course",
            index=models.Index(fields=["code"], name="main_course_code_idx"),
        ),
        migrations.AddField(
            model_name="scheduleentry",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Создано"
            ),
        ),
        migrations.AddField(
            model_name="grade",
            name="assignment_name",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Название задания"
            ),
        ),
        migrations.AddField(
            model_name="grade",
            name="date_recorded",
            field=models.DateTimeField(
                blank=True,
                help_text="Дата записи оценки в систему",
                null=True,
                verbose_name="Дата фиксации",
            ),
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "enrolled_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Дата записи",
                    ),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="main.course",
                        verbose_name="Курс",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="main.student",
                        verbose_name="Студент",
                    ),
                ),
            ],
            options={
                "verbose_name": "Запись на курс",
                "verbose_name_plural": "Записи на курсы",
                "unique_together": {("student", "course")},
            },
        ),
        migrations.AddField(
            model_name="grade",
            name="enrollment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="grades",
                to="main.enrollment",
                verbose_name="Запись на курс",
            ),
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("present", models.BooleanField(default=True, verbose_name="Присутствовал")),
                ("date", models.DateField(verbose_name="Дата")),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendance_records",
                        to="main.enrollment",
                        verbose_name="Запись на курс",
                    ),
                ),
                (
                    "lecture",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="attendance_records",
                        to="main.lecture",
                        verbose_name="Лекция",
                    ),
                ),
            ],
            options={
                "verbose_name": "Посещаемость",
                "verbose_name_plural": "Посещаемость",
            },
        ),
        migrations.AddIndex(
            model_name="attendance",
            index=models.Index(fields=["date"], name="main_attend_date_idx"),
        ),
        migrations.AddIndex(
            model_name="student",
            index=models.Index(fields=["email"], name="main_studen_email_idx"),
        ),
    ]


